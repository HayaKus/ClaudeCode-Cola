#!/usr/bin/env python3
"""
Claude Monitor Demo - 展示监控界面效果
"""

from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

console = Console()

# 创建布局
layout = Layout()
layout.split_column(
    Layout(name="header", size=3),
    Layout(name="stats", size=5),
    Layout(name="main", size=25),
    Layout(name="footer", size=3)
)

# 标题
header_text = Text("🔍 Claude Code 全局监控中心", style="bold white on blue", justify="center")
layout["header"].update(Panel(header_text, style="blue"))

# 统计信息
stats_table = Table(show_header=False, box=None, padding=(0, 2))
stats_table.add_column(justify="center")
stats_table.add_column(justify="center")
stats_table.add_column(justify="center")
stats_table.add_column(justify="center")

stats_table.add_row(
    "[cyan]总会话数[/cyan]\n[bold]1595[/bold]",
    "[green]活跃会话[/green]\n[bold]3[/bold]",
    "[yellow]TodoWrite项目[/yellow]\n[bold]194[/bold]",
    "[red]待完成任务[/red]\n[bold]145[/bold]"
)

layout["stats"].update(Panel(stats_table, title="📊 概览统计", style="cyan"))

# 主内容区域
main_layout = Layout()
main_layout.split_row(
    Layout(name="sessions", ratio=3),
    Layout(name="todos", ratio=2)
)

# 会话列表
sessions_table = Table(show_header=True, header_style="bold magenta")
sessions_table.add_column("状态", width=4)
sessions_table.add_column("项目", width=25)
sessions_table.add_column("会话ID", width=10)
sessions_table.add_column("时长", width=6)
sessions_table.add_column("消息", width=4)
sessions_table.add_column("TodoWrite", width=35)

sessions_table.add_row(
    "🟢", "Code/ClaudeCode-Cola", "7d44df89", "2h15m", "87",
    "[🔄 6/7] 正在整合所有模块并测试"
)
sessions_table.add_row(
    "🟢", "Code/Hermes", "195ada89", "1h45m", "124",
    "[🔄 5/8] 实现数据处理模块"
)
sessions_table.add_row(
    "🟢", "Code/ix-recommend", "8a3b5c21", "0h32m", "45",
    "[⏳ 0/9] 优化推荐算法性能"
)
sessions_table.add_row(
    "🔴", "Code/brics-tpp", "40ec8a1b", "3h20m", "256",
    "[✅ 6/6] 完成API接口开发"
)
sessions_table.add_row(
    "🔴", "Code/fries", "c5d3e4f2", "5h10m", "189",
    "[✅ 4/4] 修复登录认证bug"
)

main_layout["sessions"].update(Panel(sessions_table, title="💻 会话列表", style="green"))

# TodoWrite汇总
todos_table = Table(show_header=False, box=None)
todos_table.add_column()

todos_table.add_row(Text("✅ 已完成: 127  🔄 进行中: 18  ⏳ 待处理: 145", style="bold"))
todos_table.add_row("")
todos_table.add_row(Text("最新任务:", style="bold cyan"))
todos_table.add_row(Text("🔄 [ClaudeCode-Cola] 正在整合所有模块并测试", style="yellow"))
todos_table.add_row(Text("🔄 [Hermes] 实现数据处理模块", style="yellow"))
todos_table.add_row(Text("⏳ [ix-recommend] 优化推荐算法性能", style="dim"))
todos_table.add_row(Text("✅ [brics-tpp] 完成API接口开发", style="green"))
todos_table.add_row(Text("✅ [fries] 修复登录认证bug", style="green"))

main_layout["todos"].update(Panel(todos_table, title="📝 TodoWrite 汇总", style="yellow"))

layout["main"].update(main_layout)

# 页脚
footer_text = Text(
    f"进程: 3 | 按 Ctrl+C 退出 | 更新时间: {datetime.now().strftime('%H:%M:%S')}",
    style="dim",
    justify="center"
)
layout["footer"].update(Panel(footer_text, style="dim"))

# 显示
console.print(layout)