import datetime
import pandas as pd

from pandas import DataFrame, Series
from pandas.api.extensions import ExtensionArray, ExtensionDtype
from pandas.api.extensions import register_extension_dtype

from qapandas.base import QAPandasBase

from enum import Enum
import numpy as np

class QACode(Enum):
    orig = 0
    auto = 1
    manu = 2
    gapf = 3

class QADtype(ExtensionDtype):
    type = QACode
    name = "qacode"
    na_value = np.nan

    @classmethod
    def construct_from_string(cls, string):
        if string == cls.name:
            return cls()
        else:
            raise TypeError(
                "Cannot construct a '{}' from '{}'".format(cls.__name__, string)
            )

    @classmethod
    def construct_array_type(cls):
        return QAArray

register_extension_dtype(QADtype)

class QAArray(ExtensionArray):
    """
    Class wrapping a numpy array of QA bits and
    holding the array-based implementations.
    """

    _dtype = QADtype()

    def __init__(self, data):
        if isinstance(data, self.__class__):
            data = data.data
        elif not isinstance(data, np.ndarray):
            raise TypeError(
                "'data' should be array of qa objects."
            )
        elif not data.ndim == 1:
            raise ValueError(
                "'data' should be a 1-dimensional array of qa objects."
            )
        self.data = data

    @property
    def dtype(self):
        return self._dtype

    def __len__(self):
        return self.shape[0]

    def __getitem__(self, idx):
        if isinstance(idx, numbers.Integral):
            return self.data[idx]
        # array-like, slice
        if pd.api.types.is_list_like(idx):
            # for pandas >= 1.0, validate and convert IntegerArray/BooleanArray
            # to numpy array
            if not pd.api.types.is_array_like(idx):
                idx = pd.array(idx)
            dtype = idx.dtype
            if pd.api.types.is_bool_dtype(dtype):
                idx = pd.api.indexers.check_bool_array_indexer(self, idx)
            elif pd.api.types.is_integer_dtype(dtype):
                idx = np.asarray(idx, dtype="int")
        if isinstance(idx, (Iterable, slice)):
            return GeometryArray(self.data[idx])
        else:
            raise TypeError("Index type not supported", idx)

    def __setitem__(self, key, value):
        if isinstance(value, pd.Series):
            value = value.values
        if isinstance(value, (list, np.ndarray)):
            value = from_shapely(value)
        if isinstance(value, QAArray):
            if isinstance(key, numbers.Integral):
                raise ValueError("cannot set a single element with an array")
            self.data[key] = value.data
        elif isinstance(value, QACode) or _isna(value):
            if _isna(value):
                # internally only use None as missing value indicator
                # but accept others
                value = None
            if isinstance(key, (list, np.ndarray)):
                value_array = np.empty(1, dtype=object)
                value_array[:] = [value]
                self.data[key] = value_array
            else:
                self.data[key] = value
        else:
            raise TypeError(
                "Value should be either a QACode or None, got %s" % str(value)
            )

def _basic_config(self):

    # defaults
    self._raw = None
    self._qa = None
    self._qa_generated = False
    self._history = []

    TSTAMP = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    self._history.append(f"{TSTAMP} - Initiated QA Series")


class QASeries(QAPandasBase, Series):
    """
    A QADataFrame object is a pandas.DataFrame that has also has a reference of the
    raw original data, a quality flag for values and a history.
    """

    _metadata = ["_raw", "_qa", "_history"]

    def __init__(self, *args, **kwargs):
        super(QASeries, self).__init__(*args, **kwargs)

        _basic_config(self)
        self._raw = Series(*args, **kwargs)

    
    @property
    def _constructor(self):
        return QASeries

    @property
    def _constructor_expanddim(self):
        return QADataFrame

    # def _wrapped_pandas_method(self, mtd, *args, **kwargs):
    #     """Wrap a generic pandas method to ensure it returns a QASeries"""
    #     val = getattr(super(QASeries, self), mtd)(*args, **kwargs)
    #     if type(val) == Series:
    #         val.__class__ = QASeries
    #         val._history = self._history
    #         val._invalidate_qadata()
    #     return val

    # def __getitem__(self, key):
    #     return self._wrapped_pandas_method("__getitem__", key)

    def __repr__(self):
        return(f"{Series.__repr__(self)}\n\n{QAPandasBase.__repr__(self)}")



class QADataFrame(QAPandasBase, DataFrame):
    """
    A QADataFrame object is a pandas.DataFrame that has also has a reference of the
    raw original data, a quality flag for values and a history.
    """

    _metadata = ["_raw", "_qa", "_history"]

    def __init__(self, *args, **kwargs):

        super(QADataFrame, self).__init__(*args, **kwargs)

        _basic_config(self)
        self._raw = DataFrame(*args, **kwargs)
        self.logger.info("QADataFrame created")

    @property
    def _constructor(self):
        return QADataFrame

    @property
    def _constructor_sliced(self):
        return QASeries

    def __repr__(self):
        return(f"{DataFrame.__repr__(self)}\n\n{QAPandasBase.__repr__(self)}")


