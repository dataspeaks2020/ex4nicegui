from __future__ import annotations

from typing import (
    Any,
    Callable,
    List,
    Optional,
    TypeVar,
    Generic,
    cast,
    overload,
)
from typing_extensions import Self
from signe import effect
from ex4nicegui.utils.signals import (
    ReadonlyRef,
    Ref,
    to_ref,
    ref_computed,
    _TMaybeRef as TMaybeRef,
)
from nicegui import Tailwind, ui
from nicegui.elements.mixins.color_elements import (
    TextColorElement,
    QUASAR_COLORS,
    TAILWIND_COLORS,
)
from nicegui.elements.mixins.text_element import TextElement

T = TypeVar("T")

TWidget = TypeVar("TWidget")


class BindableUi(Generic[TWidget]):
    def __init__(self, element: TWidget) -> None:
        self.__element = element
        self.tailwind = Tailwind(cast(ui.element, self.__element))

    def props(self, add: Optional[str] = None, *, remove: Optional[str] = None):
        cast(ui.element, self.element).props(add, remove=remove)
        return self

    def classes(
        self,
        add: Optional[str] = None,
        *,
        remove: Optional[str] = None,
        replace: Optional[str] = None,
    ):
        cast(ui.element, self.element).classes(add, remove=remove, replace=replace)
        return self

    def style(
        self,
        add: Optional[str] = None,
        *,
        remove: Optional[str] = None,
        replace: Optional[str] = None,
    ):
        cast(ui.element, self.element).style(add, remove=remove, replace=replace)
        return self

    def tooltip(self, text: str) -> Self:
        cast(ui.element, self.element).tooltip(text)
        return self

    def add_slot(self, name: str, template: Optional[str] = None):
        """Add a slot to the element.

        :param name: name of the slot
        :param template: Vue template of the slot
        :return: the slot
        """
        return cast(ui.element, self.element).add_slot(name, template)

    @property
    def element(self):
        return self.__element

    def bind_prop(self, prop: str, ref_ui: ReadonlyRef):
        if prop == "visible":
            return self.bind_visible(ref_ui)

        if prop == "text" and isinstance(self.element, TextElement):

            @effect
            def _():
                cast(TextElement, self.element).on_text_change(ref_ui.value)

        @effect
        def _():
            element = cast(ui.element, self.element)
            element._props[prop] = ref_ui.value
            element.update()

        return self

    def bind_visible(self, ref_ui: ReadonlyRef[bool]):
        @effect
        def _():
            element = cast(ui.element, self.element)
            element.set_visibility(ref_ui.value)

        return self

    def bind_not_visible(self, ref_ui: ReadonlyRef[bool]):
        return self.bind_visible(ref_computed(lambda: not ref_ui.value))

    def on(
        self,
        type: str,
        handler: Optional[Callable[..., Any]] = None,
        args: Optional[List[str]] = None,
        *,
        throttle: float = 0.0,
        leading_events: bool = True,
        trailing_events: bool = True,
    ):
        ele = cast(ui.element, self.element)
        ele.on(
            type,
            handler,
            args,
            throttle=throttle,
            leading_events=leading_events,
            trailing_events=trailing_events,
        )

        return self

    def clear(self) -> None:
        cast(ui.element, self.element).clear()


class SingleValueBindableUi(BindableUi[TWidget], Generic[T, TWidget]):
    def __init__(self, value: TMaybeRef[T], element: TWidget) -> None:
        super().__init__(element)
        self._ref = to_ref(value)

    @property
    def value(self) -> T:
        return self._ref.value

    def bind_ref(self, ref: Ref[T]):
        @effect
        def _():
            ref.value = self._ref.value

        return self


def _bind_color(bindable_ui: SingleValueBindableUi, ref_ui: ReadonlyRef):
    @effect
    def _():
        ele = cast(TextColorElement, bindable_ui.element)
        color = ref_ui.value

        if color in QUASAR_COLORS:
            ele._props[ele.TEXT_COLOR_PROP] = color
        elif color in TAILWIND_COLORS:
            ele.classes(replace=f"text-{color}")
        elif color is not None:
            ele._style["color"] = color
        ele.update()

    return bindable_ui
