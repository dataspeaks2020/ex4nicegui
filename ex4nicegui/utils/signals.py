from signe import createSignal, effect, computed, on as signe_on
from signe.core.signal import Signal, SignalOption
from signe import utils as signe_utils
from signe.types import TSetter, TGetter
from typing import (
    Any,
    TypeVar,
    Generic,
    overload,
    Optional,
    Callable,
    cast,
    Union,
    Sequence,
)
from nicegui import ui

T = TypeVar("T")


class ReadonlyRef(Generic[T]):
    def __init__(self, getter: TGetter[T]) -> None:
        self.___getter = getter

    @property
    def value(self):
        return self.___getter()

    # def __repr__(self) -> str:
    #     return str(self.value)


class Ref(ReadonlyRef[T]):
    def __init__(
        self, getter: TGetter[T], setter: TSetter[T], signal: Optional[Signal] = None
    ) -> None:
        super().__init__(getter)
        self.___setter = setter
        self.___signal = signal

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, value: T):
        self.___setter(value)


class DescReadonlyRef(ReadonlyRef[T]):
    def __init__(self, getter: Callable[[], T], desc="") -> None:
        super().__init__(getter)
        self.__desc = desc

    @property
    def desc(self):
        return self.__desc


@overload
def ref_from_signal(getter: TGetter[T]) -> ReadonlyRef[T]:
    ...


@overload
def ref_from_signal(getter: TGetter[T], setter: TSetter[T]) -> Ref[T]:
    ...


def ref_from_signal(getter: TGetter[T], setter: Optional[TSetter[T]] = None):
    if setter is None:
        return cast(ReadonlyRef[T], ReadonlyRef(getter))

    return cast(Ref[T], Ref(getter, setter))


_TMaybeRef = Union[T, Union[Ref[T], ReadonlyRef[T]]]


def is_ref(maybe_ref: _TMaybeRef):
    return isinstance(maybe_ref, ReadonlyRef)


def to_value(maybe_ref: _TMaybeRef[T]) -> T:
    if is_ref(maybe_ref):
        return cast(ReadonlyRef, maybe_ref).value

    return cast(T, maybe_ref)


def to_ref(maybe_ref: _TMaybeRef[T]):
    if is_ref(maybe_ref):
        return cast(Ref[T], maybe_ref)

    return cast(Ref[T], ref(maybe_ref))


def ref(value: T):
    comp = (
        False
        if not isinstance(
            value,
            (
                str,
                int,
                float,
            ),
        )
        else None
    )
    # getter, setter = createSignal(value, comp)

    s = Signal(signe_utils.exec, value, SignalOption(comp))

    return cast(Ref[T], Ref(s.getValue, s.setValue, s))


@overload
def ref_computed(
    fn: Callable[[], T],
    *,
    desc="",
    debug_trigger: Optional[Callable[..., None]] = None,
    priority_level: int = 1,
) -> ReadonlyRef[T]:
    ...


@overload
def ref_computed(
    fn=None,
    *,
    desc="",
    debug_trigger: Optional[Callable[..., None]] = None,
    priority_level: int = 1,
) -> Callable[[Callable[..., T]], ReadonlyRef[T]]:
    ...


def ref_computed(
    fn: Optional[Callable[[], T]] = None,
    *,
    desc="",
    debug_trigger: Optional[Callable[..., None]] = None,
    priority_level: int = 1,
) -> Union[ReadonlyRef[T], Callable[[Callable[..., T]], ReadonlyRef[T]]]:
    kws = {
        "debug_trigger": debug_trigger,
        "priority_level": priority_level,
    }

    if fn:
        getter = computed(fn, **kws)
        return cast(DescReadonlyRef[T], DescReadonlyRef(getter, desc))
    else:

        def wrap(fn: Callable[[], T]):
            return ref_computed(fn, **kws)

        return wrap


class effect_refreshable:
    def __init__(
        self, fn: Callable, refs: Union[ReadonlyRef, Sequence[ReadonlyRef]] = []
    ) -> None:
        self._fn = fn
        self._refs = refs if isinstance(refs, Sequence) else [refs]
        self()

    @staticmethod
    def on(refs: Union[ReadonlyRef, Sequence[ReadonlyRef]]):
        def warp(
            fn: Callable,
        ):
            return effect_refreshable(fn, refs)

        return warp

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        re_func = ui.refreshable(self._fn)

        first = True

        def runner():
            nonlocal first
            if first:
                re_func()
                first = False
                return

            re_func.refresh()

        if len(self._refs) == 0:
            runner = effect(runner)
        else:
            runner = on(self._refs)(runner)

        return runner


def on(refs: Union[ReadonlyRef, Sequence[ReadonlyRef]]):
    if not isinstance(refs, Sequence):
        refs = [refs]

    getters = [getattr(r, "_ReadonlyRef___getter") for r in refs]

    def wrap(fn: Callable):
        return signe_on(getters, fn)

    return wrap
