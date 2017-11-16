import itertools
import sys
import numpy as np

# NOTE-TO-SELF: Uses the following csv format:
# Student number, stage string, [problem number, template number, score, time]*
def readProbletResultData(filename, byTemplate=False):
  """
  Read the datafile in and parse into a dictionary of dictionaries.
  Each upper-level dictionary corresponds with a student.  Each
  student has a dictionary of problem results.  When 'byTemplate' is
  False (the default) then the problems are stored by problem number.
  When 'byTemplate' is True then the problems are stored by template
  number.  There is no filtering based on problem type or whether or
  not there are overlaps among students in this routine -- it just
  returns what it reads.

  Expected format:
  Student number, stage string, [problem number, template number, score, time]*
  """
  # Open the file, read it into a list of text strings, then close the file
  probletResultFile = open(filename,'r')
  probletResultLines = probletResultFile.readlines()
  probletResultFile.close()

  # Loop through each line, assuming that each line represents student
  # records.  The routine is smart enough to understand multiple lines
  # for the same student.
  studentResultDict = {}
  for line in probletResultLines:
    # Parse the line into a list of fields by using a comma delimeter
    fields = line.split(',')

    # Use the studentID as the key into the student dictionary.
    # the testType is set here but never used (later, maybe?)
    studentID = int(fields[0])
    testType = fields[1]

    # If this student is already in the dictionary,
    # extend his or her problet results.  Otherwise
    # start a new entry and add these results to that
    problemResults = {}
    if not studentID in studentResultDict:
      studentResultDict[studentID] = problemResults
    else:
      problemResults = studentResultDict[studentID]

    # Add all problet results you find to the current
    # dictionary.  Results come in groups of six fields
    for idx in xrange(2,len(fields),4):
      if (idx+3) < len(fields):
        rec = {}

        # Index by template number if asked to do
        # so and by problet number otherwise.
        problemIndex = -1
        if byTemplate:
          problemIndex = int(fields[idx+1]) # template ID
        else:
          problemIndex = int(fields[idx])   # problet ID
          
        rec['problem'] = int(fields[idx])
        rec['template'] =  int(fields[idx+1])
        rec['score'] = float(fields[idx+2])
        rec['time'] = int(fields[idx+3])

        problemResults[problemIndex] = rec

  return studentResultDict



def printProbletDataSet(dataset):
  """
  A convenience function to print a student/problem dataset in a
  'pretty' way.
  """
  print "Student ID".ljust(10), "Problem/Template ID"
  print "----------",           "-------------------"
  for student in dataset:
    problems = list(set(dataset[student].keys()))
    problems.sort()
    
    print str(student).ljust(10),
    for problem in problems:
      print str(problem) + ",",
    print
  print

  

def cleanupForStudentAnalysis(results, probletSubset):
  """
  Filter the data for doing student-based analysis:
    * Strip out students for whom there's no response on
      the specified problems;
    * Set the 'testResult' to True for each problem that
      the student got entirely correct;
    * Organize as a list of tuples, where each tuple is a student and
      the tuple is the vector of results of how that student performed
      on each problem;
    * Throw out duplicates of specific result configurations.
  """
  # Use only students that have taken the specified problems
  students = []
  for student in results:
    if probletSubset.issubset(set(results[student])):
      students.append(student)

  students.sort()
  problems = list(probletSubset)
  problems.sort()

  # For each problem and student, give a 'True' if the student
  # got *all* instances of that problem correct and 'False' otherwise.
  testDict = {}
  for student in students:
    resultList = []
    for problem in problems:
      resultList.append(results[student][problem]['score'])
    testResult = tuple(resultList)

    # Ensures only one copy of tests with a specific result configuration
    # is retained (i.e., reserves uniqueness of result)
    testDict[testResult] =  (testResult, sum(testResult), student) 
    
  return testDict.values()     


def cleanupForProbletAnalysis(results, probletSubset):
  """
  Filter the data for doing problem-based analysis:
    * Strip out students for whom there's no response on
      the specified problems;
    * Set the 'testResult' to True for each problem that
      the student got entirely correct;
    * Organize as a list of tuples, where each tuple is a problem and
      the tuple is the vector of results of what students solved
      that problem correctly;
    * Throw out duplicates of specific result configurations.
  """
  # Use only students that have taken the specified problets
  students = []
  for student in results:
    if probletSubset.issubset(set(results[student])):
      students.append(student)

  students.sort()
  problems = list(probletSubset)
  problems.sort()
  
  # For each problem and student, give a 'True' if the student
  # got *all* instances of that problem correct and 'False' otherwise.
  testDict = {}
  for problem in problems:
    resultList = []
    for student in students:
      # Paul, did you mean to include when correct < total or should this have been correct >= total?
      resultList.append( results[student][problem]['score'] < 1.0 )
    testResult = tuple(resultList)

    # Ensures only one copy of tests with a specific result configuration
    # is retained (i.e., reserves uniqueness of result)
    testDict[testResult] =  (testResult, sum(testResult), problem) 
    
  return testDict.values()     

        

def compareOnOne(candidate, test):
  """
  A simple multiobjective game interaction function.  Given a vector a numbers for
  the candidate and also for the test, chose the dimension in which the test is greatest
  and return True if the candidate is at least as big in that dimension.
  """
  m = np.argmax(test)
  retVal = False
  if candidate[m] >= test[m]:
    retVal = True
  return retVal


def generateFakeData(n=5, d=2):
  """
  For testing purposes, this generates a fake test set by
  playing the compare-on-one game between many candidate
  and test strategies.  These strategies are selected by
  taking every permutation of vectors of integers between
  0 and n of dimension d.

  It returns a list of tuples.  Each tuple contains:
    0)  a tuple representing the results against the candidate strategies;
    1)  an integer containing the total number of successes in those results;
    2)  the test strategy that obtained those results.
  """
  testDict = {}
  for testStrategy in itertools.permutations(range(n),d):
    resultList = []
    for candidateStrategt in itertools.permutations(range(n),d):
      resultList.append(compareOnOne(candidateStrategt,testStrategy))
    testResult = tuple(resultList)

    # Ensures only one copy of tests with a specific result configuration
    # is retained (i.e., reserves uniqueness of result)
    testDict[testResult] =  (testResult, sum(testResult), testStrategy) 
    
  return testDict.values()


def tupleAnd(t1,t2):
  """
  A simple wrapper function that compares two tuples using logical And.
  It assumes the tuples are the same dimensionality and contain Booleans.
  """
  return map(lambda a,b: a and b,  t1,  t2)


def filterTests(tests):
  """
  This function sorts and filters the data to ensure no unnecessary redundancies
  in configuration of results and also sorts them in order of the number of
  successful tests.
  """
  #  tests = list(set(generateFakeData(4,2)))
  tests.sort(key=lambda x: x[1])
  tests.reverse()

  keeping  = []
  keeping.append(tests.pop(0))
  keeping.append(tests.pop(0))
  
  for test in tests:
    t1 = keeping[-1][0]
    t2 = keeping[-2][0]
    t3 = test[0]
    if not (t3 == tupleAnd(t1,t2)):
      keeping.append(test)

  return keeping


def mooCompare(v1, v2):
  """
  Compare two vectors in a multiobjective sense.  This routine returns two values.
  The first indicates whether or not the two vectors can be compared in terms of
  total ordering.  The second returns the result of the comparison, assuming they
  can be compared.  If the two vectors are equal, it returns True and 0.  If the
  first vector Pareto dominates the second, return True and 1.  If the second
  Pareto dominates the first, return True and -1.  Otherwise it returns False and
  0, though the zero value is meaningless in this case.
  """
  a = np.array(v1)
  b = np.array(v2)  

  if all(a==b):
    return True, 0
  elif all(a >= b) and any(a > b):
    return True, 1
  elif all(b >= a) and any(b > a):
    return True, -1
  else:
    return False, 0
  
  
    
def extractDimensions(filteredTests):
  """
  Construct the geometric dimensions of interaction comparisons
  according the Anthony Bucci's dimensions extraction method from:

    Bucci, Pollack, & de Jong (2004).  "Automated Extraction
    of Problem Structure".  In Proceedings of the 2004 Genetic
    and Evolutionary Computation Conference.

  The routine returns a list of dimensions.  Each dimension
  corresponds to an underlying objective of the problem.  The
  dimension is itself a list of tests such that:

    1) All tests in a give dimension are comparable; and
    2) They are ordered in terms of Pareto dominance.
  """
  dimensions = []

  for test in filteredTests:
    wasInserted = False
    for dim in dimensions:
      comparable, compareVale = mooCompare(dim[-1][0],test[0])
      if comparable:
        dim.append(test)
        wasInserted = True
        break
      #      wasInserted = insertTestIntoDimension(dim,test)
    if not wasInserted:
      dimensions.append( [test] )

  return dimensions


def unitTest(n=4, d=2):
  """
  This is a simple unit test.
  """
  rawTests = generateFakeData(n,d)
  for test in rawTests:
    print test[1], "\t", test[0], '\t', test[2]

  print
  
  filteredTests = filterTests(rawTests)
  for test in filteredTests:
    print test[1], "\t", test[0], '\t', test[2]

  print
  
  dims = extractDimensions(filteredTests)
  for dim in dims:
    print "DIMENSION:"
    for test in dim:
      print "  ", test[1], "\t", test[0], '\t', test[2]      
    print


# NOTE TO SELF: If different topic, list pre-test template numbers in if clause
#  and change number of pre-test problems in else-clause
def getRelevantProbletSubset(byTemplate=False):
  """
  Because I'm lazy, I've hard-coded the cases I care about for these initial
  tests ... but because I'm not a horrendous programmer, I put this hard-coded
  drivel in its own routine.
  """
  probletSubset = set()
  if byTemplate:
    probletSubset = set([322, 420, 209, 424, 428, 203, 300, 622, 433, 305, 654, 310, 441, 153, 413, 126])
  else:
    probletSubset =  set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])

  return probletSubset


def analyzeProblets(probletSubset, filename="pretest-data.csv", byTemplate=False):
  """
  This function provides a dimension extraction based analysis of a dataset,
  under the assumption that we are extracting the dimensions of the underlying
  dimensions of the problem sets.   
  """
  pretestDataSet = readProbletResultData(filename, byTemplate)
  rawTests = cleanupForProbletAnalysis(pretestDataSet, probletSubset)
  filteredTests = filterTests(rawTests)
  dims = extractDimensions(filteredTests)

  return dims


def analyzeStudents(probletSubset, filename="pretest-data.csv", byTemplate=False):
  """
  This function provides a dimension extraction based analysis of a dataset,
  under the assumption that we are extracting the dimensions of the underlying
  dimensions of the students.  

  Not all students will appear in this list.  If one student performed
  precisely indentically to another, one of these was removed.  This is done
  in all such cases to ensure there are only unique student/problet result
  strings.
  """
  pretestDataSet = readProbletResultData(filename, byTemplate)
  rawTests = cleanupForStudentAnalysis(pretestDataSet, probletSubset)
  filteredTests = filterTests(rawTests)
  dims = extractDimensions(filteredTests)
    
  return dims


def summarizeProbletAnalysis(dims, byTemplate=False):
  """
  The result will be a print out of each separate problem dimension, with each
  problem in that dimension listed in order of Pareto dominance (the top one
  dominating the others, etc).  Also listed are the number of students who
  passed that test.
  """
  print "There are ", len(dims), "underlying objectives to this PROBLET data"
    
  for dim in dims:
    if byTemplate:
      print "Count \tTemplate ID"
    else:
      print "Count \tProblem ID"
      
    for test in dim:
      print "  ", test[1], "\t",
      print test[2]      
    print


def summarizeStudentAnalysis(dims):
  """
  Print out the results of dimension extraction for the sutdent analysis. The
  result will be a print out of each separate student dimension, with each
  student in that dimension listed in order of Pareto dominance (the top one
  dominating the others, etc).  Also listed are the number of problems passed
  by that student.  In addition, a binary vector is printed indicating which
  tests were passed.
  """
  print "There are ", len(dims), "underlying objectives to this STUDENT data"
  for dim in dims:
    print "Count \t Cases\t\tStudent ID"
    for test in dim:
      print "  ", test[1], "\t",
      for idx in range(len(test[0])):
        if test[0][idx]:
          sys.stdout.write('1')
        else:
          sys.stdout.write('0')
      print '\t', test[2]      
    print
  

def summarizeMaxMinDimensions(dims, testSubset):
  """
  This function attempts to provide some feedback about difficulty.  It optimizes two things.
    1. It looks across all dimensions of *learners*, finds the best learner in that dimension,
       then keeps track of which problems were *missed* by these learners.  It reports how many
       *fails* each test got with the *best* learner of each dimension as a measure of *difficulty*.
    2. It looks across all dimensions of *learners*, finds the worst learner in that dimension,
       then keeps track of which problems were *passed* by these learners.  It reports how many
       *successes* each test got with the *worst* learner of each dimension as a measure of *ease*.
  In essence:  the hardest test is the one that the best learners failed the most and the easiest
               test is the one that the worst learners passed the most.
  """
  # Initialize histograms
  n = len(testSubset)
  hardHist = [0] * n
  easyHist = [0] * n

  for dim in dims:
    bestLearnerInDim = dim[0]
    worstLearnerInDim = dim[-1]

    for idx in range(n):
      if not bestLearnerInDim[0][idx]:
        hardHist[idx] += 1
      if worstLearnerInDim[0][idx]:
        easyHist[idx] += 1

  # Print header
  print "".ljust(5),
  for test in testSubset:
    print str(test).center(5),
  print
  print "".ljust(5),
  for test in testSubset:
    print ''.center(5,'='),
  print

  maxVal = max(hardHist)
  print "Hard".ljust(5),
  for idx in range(n):
    if hardHist[idx] == maxVal:
      print ("*"+str(hardHist[idx])).center(5),
    else:
      print str(hardHist[idx]).center(5),
  print
  
  maxVal = max(easyHist)
  print "Easy".ljust(5),
  for idx in range(n):
    if easyHist[idx] == maxVal:
      print ("*"+str(easyHist[idx])).center(5),
    else:
      print str(easyHist[idx]).center(5),
  print

  
# NOTE-TO-SELF: python deca.py file.csv y/n  (y for template number, n for problem number)
if __name__ == '__main__':
  filename = "pretest-data.csv"
  byTemplate = False
  probletSubset = None

  try:
    filename = sys.argv[1]
    byTemplate = sys.argv[2].strip().lower()[0] in set(['y','t','1'])
  except:
    pass
  
  if probletSubset==None:
    probletSubset = getRelevantProbletSubset(byTemplate)

  print "Problet Dimensional Analysis:".upper()
  print ''.ljust(70,'-')
  print "  Each grouping below represents a distinct 'concept' discovered in the problet data."
  print "  The problems in that dimension are listed in Pareto dominance order, such that the"
  print "  top problem strictly dominates the ones under it.  Only the top-most problem in"
  print "  each dimension provides any *distinctions* in student performance."
  print ''.ljust(70,'-')

  probletDims = analyzeProblets(probletSubset,filename,byTemplate)
  summarizeProbletAnalysis(probletDims,byTemplate)
  print

  print "Student Dimensional Analysis:".upper()
  print ''.ljust(70,'-')
  print "  Each grouping below represents a distinct 'type' of student performance discovered"
  print "  The students in that dimension are listed in Pareto dominance order, such that the"
  print "  top student strictly dominates the ones under it.  The top student in each group"
  print "  might be seen as the one who mastered that concept the best, while the bottom might"
  print "  be seen as the one who mastered it the least."
  print ''.ljust(70,'-')
  studentDims = analyzeStudents(probletSubset,filename,byTemplate)
  summarizeStudentAnalysis(studentDims)
  print

  print "Problem Difficulty Analysis (*):".upper()
  print ''.ljust(70,'-')
  print "  For the 'Hard' row, we count the number of times the *best* student"
  print "  in each dimension misses that Problem.  The bigger the number, the harder."
  print
  print "  For the 'easy' row, we count the number of times the *worst* student"
  print "  in each dimension passes that Problem.  The bigger the number, the easier."
  print
  print "  The optima in each case is indicated by '*'."
  print ''.ljust(70,'-')
  summarizeMaxMinDimensions(studentDims,probletSubset)
  print
