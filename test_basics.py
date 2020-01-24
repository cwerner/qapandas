from qapandas import QADataFrame, QASeries
import pandas as pd

import logging
import sys

import pytest

@pytest.fixture
def s():
    return QASeries({'a': [1,2,3,4]})

@pytest.fixture
def df():
    return QADataFrame({'a': [1,2,3,4], 
                        'b': ['a', 'a', 'c', 'b'], 
                        'c': [.1, .1, .2, .1]})

# simple type checking
def test_instance_type_qadataframe(df):
    assert type(df) == QADataFrame

def test_instance_transpose_qadataframe(df):
    assert type(df.T) == QADataFrame

def test_instance_slice_qadataframe1(df):
    assert type(df.iloc[1:3]) == QADataFrame

def test_instance_slice_qadataframe2(df):
    assert type(df.iloc[1]) == QASeries

def test_instance_type_qaseries(s):
    assert type(s) == QASeries

def test_instance_type_qaseries(df):
    assert type(df.a) == QASeries

# this fails as dtype is object and name is missing on df.a
def test_instance_type_qadataframe_qaseries(df, s):
    print(df.a)
    print(pd.Series({'a': [1,2,3,4]}))
    assert df.a == pd.Series({'a': [1,2,3,4]})

