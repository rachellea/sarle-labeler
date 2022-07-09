#equality_checks.py
#Copyright (c) 2020 Rachel Lea Ballantyne Draelos

#MIT License

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE

#Function for testing equality of dataframes
def dfs_equal(df1, df2):
    assert df1.columns.values.tolist()==df2.columns.values.tolist()
    assert df1.index.values.tolist()==df2.index.values.tolist()
    for row in df1.index.values.tolist():
        for col in df1.columns.values.tolist():
            assert df1.at[row,col] == df2.at[row,col], 'Error at ['+str(row)+','+str(col)+']'
    return True

#Function for testing equality of arrays
def arrays_equal(array1, array2, tol =  1e-6):
    """Check if arrays are equal within tolerance <tol>
    Note that if <tol>==0 then check that arrays are identical.
    Because the following stuff doesn't work at all:
    numpy.testing.assert_almost_equal 
    np.all
    np.array_equal
    np.isclose"""
    assert array1.shape == array2.shape
    if len(array1.shape)==1: #one-dimensional
        for index in range(len(array1)):
            if tol == 0:
                assert array1[index] == array2[index]
            else:
                assert abs(array1[index] - array2[index]) < tol
    else: #two-dimensional
        for row in range(array1.shape[0]):
            for col in range(array1.shape[1]):
                if tol == 0:
                    assert array1[row,col] == array2[row,col]
                else:
                    assert abs(array1[row,col] - array2[row,col]) < tol
    return True
