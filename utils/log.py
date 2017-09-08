from .base import ChoiceEnum


class LogLevel(ChoiceEnum):
    Quite = "quite"
    Panic = "panic"
    Fatal = "fatal"
    Error = "error"
    Warning = "warning"
    Info = "info"
    Verbose = "verbose"
    Debug = "debug"
    Trace = "trace"
