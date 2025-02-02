from typing import Any, Callable, Optional
from dataclasses import dataclass
from nicegui.dataclasses import KWONLY_SLOTS
from nicegui.events import handle_event, UiEventArguments
from nicegui.element import Element


_Chart_Click_Args = [
    "componentType",
    "seriesType",
    "seriesIndex",
    "seriesName",
    "name",
    "dataIndex",
    "data",
    "dataType",
    "value",
    "color",
]


@dataclass(**KWONLY_SLOTS)
class EChartsClickEventArguments(UiEventArguments):
    componentType: str
    seriesType: str
    seriesIndex: int
    seriesName: str
    name: str
    dataIndex: int
    data: dict
    dataType: Optional[str]
    value: Any
    color: str


class echarts(Element, component="ECharts.js"):
    def __init__(self, options: dict) -> None:
        super().__init__()
        self._props["options"] = options

    def update_options(self, options: dict, opts: Optional[dict] = None):
        """update chart options

        Args:
            options (dict): chart setting options dict
            opts (Optional[dict], optional): update options. Defaults to None.
            ```python
                {
                    'notMerge':False,
                    'lazyUpdate':False,
                    'silent':False,
                    'replaceMerge': None,
                }
            ```
            [open echarts setOption docs](https://echarts.apache.org/zh/api.html#echartsInstance.setOption)

        """
        self.run_method("updateOptions", options, opts)
        self.update()
        return self

    def on_chart_click(
        self, handler: Optional[Callable[[EChartsClickEventArguments], Any]]
    ):
        def inner_handler(e):
            args = e.args
            handle_event(
                handler,
                EChartsClickEventArguments(
                    sender=self,
                    client=self.client,
                    componentType=args["componentType"],
                    seriesType=args["seriesType"],
                    seriesIndex=args["seriesIndex"],
                    seriesName=args["seriesName"],
                    name=args["name"],
                    dataIndex=args["dataIndex"],
                    data=args["data"],
                    dataType=args["dataType"] if "dataType" in args else None,
                    value=args["value"],
                    color=args["color"],
                ),
            )

        self.on("chartClick", inner_handler, _Chart_Click_Args)

    def on_chart_click_blank(
        self, handler: Optional[Callable[[UiEventArguments], Any]]
    ):
        def inner_handler(e):
            handle_event(
                handler,
                UiEventArguments(
                    sender=self,
                    client=self.client,
                ),
            )

        self.on("chartClickBlank", inner_handler, _Chart_Click_Args)
