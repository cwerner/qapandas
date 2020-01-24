import logging

class LoggerMixin(object):
    @property
    def logger(self):
        name = '.'.join([
            self.__module__,
            self.__class__.__name__
        ])
        return logging.getLogger(name)

class QAPandasBase(LoggerMixin, object):

    def _generate_qadata(self):
        print("Doing stuff...")
        self._qa_generated = True

    def _invalidate_qadata(self):
        """
        Indicates that the qa sections should be re-built next
        time it's requested.
        """
        self._raw = None
        self._qa = None
        self._qa_generated = False

    @property
    def history(self):
        """Returns the recorded metadata/ history of the qa data class"""
        return '\n'.join(self._history)

    @property
    def raw(self):
        """Returns the raw/ original data of the qa data class"""
        return self._raw

    def __repr__(self):
        _qa_str = f"[QA]: {self._qa}" if self._qa else "[QA]: not set"
        _hist = '\n'+'\n'.join(self._history)
        _history = f"[History]: {_hist}" if self._history else "[History]: empty"
        return f"{_qa_str}\n{_history}"
