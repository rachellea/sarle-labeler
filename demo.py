#demo.py
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

from src import run_sarle

def run_rules_demo():
    """Apply the SARLE-Rules method to the OpenI CXR report dataset."""
    #Mark ambiguous findings positive:
    run_sarle.generate_labels('rules','openi_cxr',False,'pos',True)

    #Mark ambiguous findings negative:
    run_sarle.generate_labels('rules','openi_cxr',False,'neg',True)


def run_hybrid_demo():
    """Apply the SARLE-Hybrid method to the OpenI CXR report dataset"""
    #Mark ambiguous findings positive:
    run_sarle.generate_labels('hybrid','openi_cxr',False,'pos',True)

    #Mark ambiguous findings negative:
    run_sarle.generate_labels('hybrid','openi_cxr',False,'neg',True)


if __name__=='__main__':
    run_rules_demo()
    run_hybrid_demo()