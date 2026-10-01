# -*- coding: utf-8 -*-
# IronPython-safe debug log (no stdlib os/traceback). Tail artifact_cleaner_debug.log while CE runs.

from version import PLUGIN_VERSION

_LOG_NAME = "artifact_cleaner_debug.log"


def log_path():
    try:
        from System.IO import Path, File

        here = Path.GetDirectoryName(__file__)
        if here:
            return Path.Combine(here, _LOG_NAME)
    except Exception:
        pass
    return _LOG_NAME


def write(level, message):
    line = "[{0}] v{1} {2}: {3}\n".format(
        _now(), PLUGIN_VERSION, level, message
    )
    try:
        print(line.rstrip())
    except Exception:
        pass
    try:
        from System.IO import File, FileMode, FileAccess, FileShare, StreamWriter
        from System.Text import Encoding

        path = log_path()
        fs = File.Open(path, FileMode.Append, FileAccess.Write, FileShare.ReadWrite)
        try:
            sw = StreamWriter(fs, Encoding.UTF8)
            try:
                sw.Write(line)
                sw.Flush()
            finally:
                sw.Close()
        finally:
            fs.Close()
    except Exception as ex:
        try:
            print("debug_log write failed: {0}".format(ex))
        except Exception:
            pass


def write_exception(phase, ex):
    write(
        "ERROR",
        "phase={0} type={1} msg={2}".format(phase, type(ex).__name__, ex),
    )
    for frame in _stack_lines():
        write("TRACE", frame)


def _stack_lines():
    out = []
    try:
        import sys

        _t, _v, tb = sys.exc_info()
        while tb is not None:
            f = tb.tb_frame
            co = f.f_code
            out.append(
                'File "{0}", line {1}, in {2}'.format(
                    co.co_filename, tb.tb_lineno, co.co_name
                )
            )
            tb = tb.tb_next
    except Exception as ex:
        out.append("(stack walk failed: {0})".format(ex))
    if not out:
        out.append("(no traceback frames)")
    return out


def _now():
    try:
        from System import DateTime

        return DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff")
    except Exception:
        return "?"


def clear():
    """Truncate log at session start (optional)."""
    try:
        from System.IO import File

        path = log_path()
        if File.Exists(path):
            File.WriteAllText(path, "")
    except Exception:
        pass
