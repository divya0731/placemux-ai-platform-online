"""
seed.py — PlaceMux item bank seeder
====================================
Drops and recreates all tables, then seeds the item bank with:
  • CSE001 — Python Advanced & OOPs (15 items: 5 Easy / 5 Medium / 5 Hard)
  • CSE002 — Data Structures & Algorithms (15 items: 5 Easy / 5 Medium / 5 Hard)
  • ECE001 — Digital Electronics & Logic Design (10 items: 4 Easy / 3 Medium / 3 Hard)
  • ECE002 — Embedded C & Microcontrollers (10 items: 4 Easy / 3 Medium / 3 Hard)

IRT parameters follow the 3PL model:
  a_param  — discrimination: 0.9–1.5 (SME-seeded)
  b_param  — difficulty: Easy ≈ -1.5 to -1.0 | Medium ≈ -0.2 to 0.2 | Hard ≈ 1.2 to 1.8
  c_param  — guessing: 0.25 for all MCQs (4 options)
  exposure_cap — 50 (default; lower for hard items)

Min pool size before adaptive delivery: 10 items per competency.
Current seeded pool sizes all meet or exceed this threshold.
"""

from database import engine, Base, SessionLocal
from models.candidate import Candidate
from models.questions import Question
from models.response import Response
from models.proctoring import ProctoringLog
from models.candidate_score import CandidateScore


def seed_db():
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    questions = [

        # ════════════════════════════════════════════════════════════
        #  CSE001 — Python Advanced & OOPs
        # ════════════════════════════════════════════════════════════

        # ── Easy (b ≈ -1.2 to -1.6) ────────────────────────────────
        Question(
            question_id="Q001", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Syntax & Basics",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="What is Python?",
            option_a="A venomous snake",
            option_b="A high-level interpreted programming language",
            option_c="A relational database engine",
            option_d="A low-level operating system kernel",
            correct_answer="B",
            distractor_rationale="A: common misconception (name origin); C/D: wrong category.",
            a_param=1.2, b_param=-1.5, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q002", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Syntax & Basics",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="Which keyword is used to define a function in Python?",
            option_a="func", option_b="function", option_c="def", option_d="define",
            correct_answer="C",
            distractor_rationale="A/B/D: keywords from other languages (JS, C-style).",
            a_param=1.1, b_param=-1.2, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q003", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Syntax & Basics",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="Which data type stores True/False values in Python?",
            option_a="String", option_b="List", option_c="Boolean", option_d="Integer",
            correct_answer="C",
            distractor_rationale="True/False are literals; bool is the type, but 'Boolean' is the accepted answer here.",
            a_param=1.0, b_param=-1.4, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q004", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Syntax & Basics",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="Which symbol starts a single-line comment in Python?",
            option_a="#", option_b="//", option_c="<!--", option_d="--",
            correct_answer="A",
            distractor_rationale="B: JavaScript/C++; C: HTML; D: SQL/Lua.",
            a_param=1.3, b_param=-1.6, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q005", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Syntax & Basics",
            bloom_level="Understand", item_type="MCQ", difficulty="Easy",
            question="Python is primarily classified as which type of language?",
            option_a="Compiled", option_b="Interpreted",
            option_c="Hardware Description", option_d="Database Query",
            correct_answer="B",
            distractor_rationale="A: C/C++ are compiled; C: VHDL/Verilog; D: SQL.",
            a_param=0.9, b_param=-1.0, c_param=0.25, exposure_cap=50,
        ),

        # ── Medium (b ≈ -0.2 to 0.2) ───────────────────────────────
        Question(
            question_id="Q006", competency_id="CSE001",
            cluster_id="Programming", sub_competency="OOP Principles",
            bloom_level="Understand", item_type="MCQ", difficulty="Medium",
            question="What does `type(lambda: None)` return in Python?",
            option_a="<class 'function'>", option_b="<class 'NoneType'>",
            option_c="<class 'lambda'>",  option_d="<class 'type'>",
            correct_answer="A",
            distractor_rationale="Lambdas are anonymous functions; their type is 'function', not a special 'lambda' class.",
            a_param=1.0, b_param=0.1, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q007", competency_id="CSE001",
            cluster_id="Programming", sub_competency="OOP Principles",
            bloom_level="Understand", item_type="MCQ", difficulty="Medium",
            question="Which decorator is used to define a class method in Python?",
            option_a="@classmethod", option_b="@static",
            option_c="@staticmethod", option_d="@method",
            correct_answer="A",
            distractor_rationale="C is for static methods (no cls); B/D do not exist in Python.",
            a_param=1.2, b_param=-0.1, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q008", competency_id="CSE001",
            cluster_id="Programming", sub_competency="OOP Principles",
            bloom_level="Apply", item_type="MCQ", difficulty="Medium",
            question="What does `*args` mean in a Python function definition?",
            option_a="Accepts a variable number of positional arguments",
            option_b="Accepts a variable number of keyword arguments",
            option_c="Defines a pointer to an argument list",
            option_d="Declares optional arguments as a tuple",
            correct_answer="A",
            distractor_rationale="B describes **kwargs; C/D are misconceptions.",
            a_param=1.1, b_param=0.0, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q009", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Syntax & Basics",
            bloom_level="Understand", item_type="MCQ", difficulty="Medium",
            question="Which of the following Python data types is mutable?",
            option_a="List", option_b="Tuple", option_c="String", option_d="FrozenSet",
            correct_answer="A",
            distractor_rationale="B/C/D are all immutable; lists support in-place modification.",
            a_param=1.3, b_param=0.2, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q010", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Decorators & Generators",
            bloom_level="Apply", item_type="MCQ", difficulty="Medium",
            question="How do you create a generator in Python?",
            option_a="By using the `yield` keyword inside a function",
            option_b="By using the `generator` keyword",
            option_c="By returning a list from any function",
            option_d="By subclassing the built-in `Generator` class",
            correct_answer="A",
            distractor_rationale="B/D do not exist; C creates a regular list-returning function.",
            a_param=0.9, b_param=-0.2, c_param=0.25, exposure_cap=50,
        ),

        # ── Hard (b ≈ 1.2 to 1.8) ──────────────────────────────────
        Question(
            question_id="Q011", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Memory Management",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="What is the primary benefit of using `__slots__` in a Python class?",
            option_a="Reduces memory by preventing creation of per-instance `__dict__`",
            option_b="Declares private attributes for encapsulation",
            option_c="Implements abstract interface methods automatically",
            option_d="Auto-generates `__get__` and `__set__` descriptors",
            correct_answer="A",
            distractor_rationale="B: use name mangling or @property; C: ABCs; D: descriptors are separate.",
            a_param=1.4, b_param=1.4, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q012", competency_id="CSE001",
            cluster_id="Programming", sub_competency="OOP Principles",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="Which metaclass method is invoked to customise class creation before the class body is executed?",
            option_a="__new__", option_b="__init__", option_c="__call__", option_d="__prepare__",
            correct_answer="D",
            distractor_rationale="__prepare__ sets up the class namespace before execution; __new__ allocates, __init__ initialises.",
            a_param=1.3, b_param=1.6, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q013", competency_id="CSE001",
            cluster_id="Programming", sub_competency="OOP Principles",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="What algorithm does Python 3 use for Method Resolution Order (MRO)?",
            option_a="C3 Linearisation", option_b="Depth-First Search",
            option_c="Breadth-First Search", option_d="Dijkstra's Shortest Path",
            correct_answer="A",
            distractor_rationale="C3 linearisation (Barry's algorithm) is the Python 3 MRO; DFS/BFS produce inconsistent orderings.",
            a_param=1.2, b_param=1.5, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q014", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Memory Management",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="What is the primary effect of the GIL (Global Interpreter Lock) in CPython?",
            option_a="Restricts execution of Python bytecode to one thread at a time",
            option_b="Accelerates mathematical operations across multiple threads",
            option_c="Prevents all memory leaks inside Python functions",
            option_d="Locks source files from simultaneous editor changes",
            correct_answer="A",
            distractor_rationale="The GIL serialises bytecode; it does not prevent memory leaks or help I/O-bound math.",
            a_param=1.5, b_param=1.7, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q015", competency_id="CSE001",
            cluster_id="Programming", sub_competency="Memory Management",
            bloom_level="Evaluate", item_type="MCQ", difficulty="Hard",
            question="What does the `weakref` module provide in Python?",
            option_a="References to objects that do not prevent garbage collection",
            option_b="Immediate deletion of variable names from local scope",
            option_c="Low-overhead multi-threaded queue implementations",
            option_d="Object layout compression to reduce memory footprint",
            correct_answer="A",
            distractor_rationale="Weak references allow GC while maintaining a reference handle; the others are unrelated.",
            a_param=1.1, b_param=1.2, c_param=0.25, exposure_cap=40,
        ),

        # ════════════════════════════════════════════════════════════
        #  CSE002 — Data Structures & Algorithms
        # ════════════════════════════════════════════════════════════

        # ── Easy ────────────────────────────────────────────────────
        Question(
            question_id="Q016", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Arrays & Strings",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="What is the time complexity of accessing an element in an array by index?",
            option_a="O(n)", option_b="O(log n)", option_c="O(1)", option_d="O(n²)",
            correct_answer="C",
            distractor_rationale="Direct index → base + offset calculation is constant time.",
            a_param=1.2, b_param=-1.5, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q017", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Arrays & Strings",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="Which data structure uses LIFO (Last In, First Out) order?",
            option_a="Queue", option_b="Stack", option_c="Linked List", option_d="Heap",
            correct_answer="B",
            distractor_rationale="Queue is FIFO; linked list and heap are neither strictly LIFO nor FIFO.",
            a_param=1.1, b_param=-1.3, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q018", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Sorting & Searching",
            bloom_level="Understand", item_type="MCQ", difficulty="Easy",
            question="Which sorting algorithm has the best average-case time complexity?",
            option_a="Bubble Sort — O(n²)", option_b="Selection Sort — O(n²)",
            option_c="Merge Sort — O(n log n)", option_d="Insertion Sort — O(n²)",
            correct_answer="C",
            distractor_rationale="Merge Sort guarantees O(n log n) in all cases; the others degrade to O(n²).",
            a_param=1.0, b_param=-1.2, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q019", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Linked Lists",
            bloom_level="Understand", item_type="MCQ", difficulty="Easy",
            question="In a singly linked list, each node contains:",
            option_a="Only data", option_b="Data and a pointer to the next node",
            option_c="Data and pointers to both next and previous nodes",
            option_d="Only a pointer to the next node",
            correct_answer="B",
            distractor_rationale="C describes a doubly linked list; A/D are incomplete.",
            a_param=1.1, b_param=-1.4, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q020", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Trees & Graphs",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="What is the maximum number of children a node can have in a binary tree?",
            option_a="1", option_b="2", option_c="3", option_d="Unlimited",
            correct_answer="B",
            distractor_rationale="Binary (bi = 2) constrains each node to at most two children.",
            a_param=1.3, b_param=-1.6, c_param=0.25, exposure_cap=50,
        ),

        # ── Medium ──────────────────────────────────────────────────
        Question(
            question_id="Q021", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Sorting & Searching",
            bloom_level="Apply", item_type="MCQ", difficulty="Medium",
            question="Binary Search requires the input array to be:",
            option_a="Unsorted", option_b="Sorted",
            option_c="Stored in a hash table", option_d="Of even length",
            correct_answer="B",
            distractor_rationale="Binary search halves the search space by comparing to the mid element, requiring sorted order.",
            a_param=1.0, b_param=0.0, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q022", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Trees & Graphs",
            bloom_level="Apply", item_type="MCQ", difficulty="Medium",
            question="In a Min-Heap, the root node always contains:",
            option_a="The maximum element", option_b="The minimum element",
            option_c="The median element",  option_d="A random element",
            correct_answer="B",
            distractor_rationale="Min-Heap property: every parent ≤ its children, so root is global minimum.",
            a_param=1.2, b_param=0.1, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q023", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Dynamic Programming",
            bloom_level="Understand", item_type="MCQ", difficulty="Medium",
            question="Which property is essential for a problem to be solvable using Dynamic Programming?",
            option_a="Optimal substructure and overlapping sub-problems",
            option_b="Greedy choice property",
            option_c="Divide-and-conquer without overlapping sub-problems",
            option_d="Linear time complexity requirement",
            correct_answer="A",
            distractor_rationale="DP needs both: optimal substructure for correctness and overlapping sub-problems for memoisation benefit.",
            a_param=1.1, b_param=-0.1, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q024", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Trees & Graphs",
            bloom_level="Analyze", item_type="MCQ", difficulty="Medium",
            question="What is the time complexity of Dijkstra's algorithm with a binary min-heap?",
            option_a="O(V²)", option_b="O(E log V)", option_c="O(V log V)", option_d="O(E + V)",
            correct_answer="B",
            distractor_rationale="Each edge relaxation triggers a heap operation (log V); total E relaxations → O(E log V).",
            a_param=1.3, b_param=0.2, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q025", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Sorting & Searching",
            bloom_level="Apply", item_type="MCQ", difficulty="Medium",
            question="Quick Sort's worst-case time complexity occurs when:",
            option_a="The array is already sorted and the pivot is always the first element",
            option_b="The array is in random order",
            option_c="The array has an even number of elements",
            option_d="The pivot is always the median element",
            correct_answer="A",
            distractor_rationale="Choosing first element as pivot on sorted data results in O(n²) due to maximally unbalanced partitions.",
            a_param=0.9, b_param=-0.2, c_param=0.25, exposure_cap=50,
        ),

        # ── Hard ────────────────────────────────────────────────────
        Question(
            question_id="Q026", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Dynamic Programming",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="What is the space complexity of the bottom-up DP solution for the 0/1 Knapsack problem (n items, capacity W)?",
            option_a="O(1)", option_b="O(n)", option_c="O(nW)", option_d="O(n²)",
            correct_answer="C",
            distractor_rationale="A standard DP table is n × W; space-optimised variants reduce to O(W) but the classic is O(nW).",
            a_param=1.4, b_param=1.4, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q027", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Trees & Graphs",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="Which algorithm detects a negative-weight cycle in a directed weighted graph?",
            option_a="Dijkstra's", option_b="Prim's", option_c="Bellman-Ford", option_d="Kruskal's",
            correct_answer="C",
            distractor_rationale="Bellman-Ford relaxes edges V-1 times; a further relaxation indicates a negative cycle.",
            a_param=1.3, b_param=1.5, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q028", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Dynamic Programming",
            bloom_level="Evaluate", item_type="MCQ", difficulty="Hard",
            question="The Longest Common Subsequence (LCS) of 'ABCDE' and 'ACE' has length:",
            option_a="2", option_b="3", option_c="4", option_d="5",
            correct_answer="B",
            distractor_rationale="LCS is 'ACE' (length 3); it is not required to be contiguous.",
            a_param=1.2, b_param=1.6, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q029", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Trees & Graphs",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="A strongly connected component (SCC) in a directed graph can be found using:",
            option_a="Prim's algorithm", option_b="Kruskal's algorithm",
            option_c="Kosaraju's or Tarjan's algorithm", option_d="Dijkstra's algorithm",
            correct_answer="C",
            distractor_rationale="Prim/Kruskal find MSTs; Dijkstra finds shortest paths; only Kosaraju/Tarjan identify SCCs.",
            a_param=1.5, b_param=1.7, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q030", competency_id="CSE002",
            cluster_id="DSA", sub_competency="Sorting & Searching",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="Which of the following sort algorithms is NOT comparison-based and can achieve O(n) time?",
            option_a="Heap Sort", option_b="Tim Sort",
            option_c="Counting Sort", option_d="Quick Sort",
            correct_answer="C",
            distractor_rationale="Counting sort distributes by key frequency (non-comparison); A/B/D are comparison-based with Ω(n log n) lower bound.",
            a_param=1.1, b_param=1.3, c_param=0.25, exposure_cap=40,
        ),

        # ════════════════════════════════════════════════════════════
        #  ECE001 — Digital Electronics & Logic Design
        # ════════════════════════════════════════════════════════════

        # ── Easy ────────────────────────────────────────────────────
        Question(
            question_id="Q031", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="Boolean Algebra",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="Which logic gate outputs HIGH only when ALL inputs are HIGH?",
            option_a="OR", option_b="AND", option_c="NAND", option_d="XOR",
            correct_answer="B",
            distractor_rationale="OR is HIGH when any input is HIGH; NAND is complement of AND; XOR is HIGH when inputs differ.",
            a_param=1.2, b_param=-1.5, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q032", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="Boolean Algebra",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="The binary representation of decimal 10 is:",
            option_a="1000", option_b="1010", option_c="1100", option_d="0110",
            correct_answer="B",
            distractor_rationale="8+2=10 → 1010₂; 1000=8; 1100=12; 0110=6.",
            a_param=1.1, b_param=-1.3, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q033", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="Combinational Circuits",
            bloom_level="Understand", item_type="MCQ", difficulty="Easy",
            question="A Full Adder has how many inputs?",
            option_a="1", option_b="2", option_c="3", option_d="4",
            correct_answer="C",
            distractor_rationale="Full Adder: A, B, and Carry-in (Cin); Half Adder has only A and B.",
            a_param=1.0, b_param=-1.4, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q034", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="Sequential Circuits",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="Which flip-flop toggles its output on every clock edge?",
            option_a="SR Flip-Flop", option_b="D Flip-Flop", option_c="T Flip-Flop", option_d="JK Flip-Flop",
            correct_answer="C",
            distractor_rationale="T (Toggle) flip-flop: Q_next = NOT Q when T=1; SR and D have different behaviour.",
            a_param=1.3, b_param=-1.2, c_param=0.25, exposure_cap=50,
        ),

        # ── Medium ──────────────────────────────────────────────────
        Question(
            question_id="Q035", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="Minimisation (K-Map)",
            bloom_level="Apply", item_type="MCQ", difficulty="Medium",
            question="K-Map grouping rules require groups to be of size:",
            option_a="Any integer", option_b="Powers of 2 (1, 2, 4, 8, …)",
            option_c="Prime numbers only", option_d="Even numbers only",
            correct_answer="B",
            distractor_rationale="K-Map groups must be powers of 2 for valid Boolean minimisation.",
            a_param=1.1, b_param=0.0, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q036", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="Sequential Circuits",
            bloom_level="Analyze", item_type="MCQ", difficulty="Medium",
            question="A 4-bit binary ripple counter uses how many flip-flops?",
            option_a="2", option_b="8", option_c="4", option_d="16",
            correct_answer="C",
            distractor_rationale="Each flip-flop stores one bit; a 4-bit counter needs exactly 4 flip-flops.",
            a_param=1.2, b_param=0.1, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q037", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="FSMs",
            bloom_level="Analyze", item_type="MCQ", difficulty="Medium",
            question="A Mealy machine's output depends on:",
            option_a="Current state only",
            option_b="Current state and current input",
            option_c="Next state only",
            option_d="Input only",
            correct_answer="B",
            distractor_rationale="Mealy: output = f(state, input); Moore: output = f(state) only.",
            a_param=1.0, b_param=-0.1, c_param=0.25, exposure_cap=50,
        ),

        # ── Hard ────────────────────────────────────────────────────
        Question(
            question_id="Q038", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="Minimisation (K-Map)",
            bloom_level="Evaluate", item_type="MCQ", difficulty="Hard",
            question="Which Boolean expression is the minimal SOP for f(A,B,C) = Σm(1,3,5,7)?",
            option_a="A'B + AB'", option_b="C", option_c="A + B", option_d="A ⊕ B",
            correct_answer="B",
            distractor_rationale="Minterms 1,3,5,7 all have C=1 regardless of A and B, so the minimal SOP is simply C.",
            a_param=1.4, b_param=1.4, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q039", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="Sequential Circuits",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="Setup time violation in a flip-flop causes:",
            option_a="Increased propagation delay", option_b="Metastability",
            option_c="Reduced power consumption",  option_d="Logic 0 output always",
            correct_answer="B",
            distractor_rationale="When data changes too close to the clock edge, the FF may enter a metastable state with undefined output.",
            a_param=1.3, b_param=1.6, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q040", competency_id="ECE001",
            cluster_id="Digital_Electronics", sub_competency="FSMs",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="How many states are needed in a minimal DFA that accepts binary strings divisible by 3?",
            option_a="2", option_b="3", option_c="4", option_d="8",
            correct_answer="B",
            distractor_rationale="States track remainder mod 3: {0, 1, 2}; state 0 is accepting. Three states suffice.",
            a_param=1.5, b_param=1.8, c_param=0.25, exposure_cap=40,
        ),

        # ════════════════════════════════════════════════════════════
        #  ECE002 — Embedded C & Microcontrollers
        # ════════════════════════════════════════════════════════════

        # ── Easy ────────────────────────────────────────────────────
        Question(
            question_id="Q041", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="C for Embedded",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="Which qualifier prevents a variable from being optimised away by the compiler in embedded C?",
            option_a="const", option_b="static", option_c="volatile", option_d="extern",
            correct_answer="C",
            distractor_rationale="'volatile' tells the compiler not to cache the variable; used for hardware registers.",
            a_param=1.2, b_param=-1.5, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q042", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="GPIO & Peripherals",
            bloom_level="Understand", item_type="MCQ", difficulty="Easy",
            question="GPIO stands for:",
            option_a="General Protocol Input/Output",
            option_b="General Purpose Input/Output",
            option_c="Graphics Processing I/O",
            option_d="Global Peripheral Interface Operations",
            correct_answer="B",
            distractor_rationale="GPIO = General Purpose Input/Output — configurable digital pins on a microcontroller.",
            a_param=1.1, b_param=-1.3, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q043", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="Interrupts & Timers",
            bloom_level="Understand", item_type="MCQ", difficulty="Easy",
            question="An ISR (Interrupt Service Routine) should be:",
            option_a="As long as possible to handle all events",
            option_b="Short and fast to minimise latency",
            option_c="Called only from the main loop",
            option_d="Blocking until the task is fully complete",
            correct_answer="B",
            distractor_rationale="ISRs should be minimal to avoid blocking other interrupts; deferred work goes to task queues.",
            a_param=1.0, b_param=-1.4, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q044", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="Communication Protocols (I2C/SPI/UART)",
            bloom_level="Remember", item_type="MCQ", difficulty="Easy",
            question="How many wires does a basic UART communication link require (excluding power/ground)?",
            option_a="1", option_b="2", option_c="4", option_d="6",
            correct_answer="B",
            distractor_rationale="UART uses TX and RX (2 wires); SPI needs 4 (MOSI, MISO, SCK, CS); I2C uses 2 (SDA, SCL).",
            a_param=1.3, b_param=-1.2, c_param=0.25, exposure_cap=50,
        ),

        # ── Medium ──────────────────────────────────────────────────
        Question(
            question_id="Q045", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="Interrupts & Timers",
            bloom_level="Apply", item_type="MCQ", difficulty="Medium",
            question="Which timer mode generates a fixed-frequency PWM signal on an AVR microcontroller?",
            option_a="Normal Mode", option_b="CTC (Clear Timer on Compare) Mode",
            option_c="Fast PWM Mode", option_d="Input Capture Mode",
            correct_answer="C",
            distractor_rationale="Fast PWM mode uses the timer to generate hardware PWM; CTC generates square waves; Input Capture measures pulse width.",
            a_param=1.1, b_param=0.0, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q046", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="Communication Protocols (I2C/SPI/UART)",
            bloom_level="Analyze", item_type="MCQ", difficulty="Medium",
            question="In I2C, the address of a slave device is transmitted:",
            option_a="Only once at power-on",
            option_b="At the beginning of every transaction after the START condition",
            option_c="Only when the master requests data",
            option_d="Broadcast to all slaves simultaneously without addressing",
            correct_answer="B",
            distractor_rationale="Every I2C transaction: START → 7-bit address + R/W bit → ACK → data → STOP.",
            a_param=1.2, b_param=0.1, c_param=0.25, exposure_cap=50,
        ),
        Question(
            question_id="Q047", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="RTOS Basics",
            bloom_level="Understand", item_type="MCQ", difficulty="Medium",
            question="In an RTOS, a semaphore is primarily used for:",
            option_a="Storing task priorities",
            option_b="Synchronisation and mutual exclusion between tasks",
            option_c="Allocating heap memory to tasks",
            option_d="Setting CPU clock frequency dynamically",
            correct_answer="B",
            distractor_rationale="Semaphores control access to shared resources; priorities are set in task descriptors; heap is managed by the memory allocator.",
            a_param=1.0, b_param=-0.1, c_param=0.25, exposure_cap=50,
        ),

        # ── Hard ────────────────────────────────────────────────────
        Question(
            question_id="Q048", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="C for Embedded",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="What is the effect of declaring a function pointer as `void (*fp)(void)` and calling it without initialisation?",
            option_a="Calls the null function stub safely",
            option_b="Causes undefined behaviour (likely a crash/fault)",
            option_c="Compiler error at compilation time",
            option_d="The CPU skips the call silently",
            correct_answer="B",
            distractor_rationale="An uninitialised pointer holds garbage; dereferencing it is undefined behaviour in C, usually causing a hard fault.",
            a_param=1.4, b_param=1.4, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q049", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="RTOS Basics",
            bloom_level="Analyze", item_type="MCQ", difficulty="Hard",
            question="Priority inversion in an RTOS occurs when:",
            option_a="Two tasks have the same priority",
            option_b="A low-priority task holds a resource needed by a high-priority task",
            option_c="The scheduler promotes tasks above their assigned priority",
            option_d="A task's stack overflows into another task's region",
            correct_answer="B",
            distractor_rationale="Priority inversion: high-priority task blocks on a resource held by a low-priority task; resolved by priority inheritance.",
            a_param=1.3, b_param=1.6, c_param=0.25, exposure_cap=40,
        ),
        Question(
            question_id="Q050", competency_id="ECE002",
            cluster_id="Embedded_Systems", sub_competency="Communication Protocols (I2C/SPI/UART)",
            bloom_level="Evaluate", item_type="MCQ", difficulty="Hard",
            question="When selecting between I2C and SPI for a high-speed ADC sampling at 1 MSPS, which protocol is more appropriate and why?",
            option_a="I2C — because it uses fewer wires",
            option_b="SPI — because it is full-duplex with no overhead address byte, supporting higher throughput",
            option_c="UART — because it has hardware flow control",
            option_d="I2C — because it supports multi-master natively",
            correct_answer="B",
            distractor_rationale="SPI has no start/stop overhead and is full-duplex; I2C is slower (max ~3.4 MHz Fast-mode Plus) and half-duplex.",
            a_param=1.5, b_param=1.7, c_param=0.25, exposure_cap=40,
        ),
    ]

    try:
        db.add_all(questions)
        db.commit()
        print(f"Successfully seeded {len(questions)} IRT questions across 4 competencies!")
        print("  CSE001 (Python): 15 items (5E/5M/5H)")
        print("  CSE002 (DSA):    15 items (5E/5M/5H)")
        print("  ECE001 (Digital): 10 items (4E/3M/3H)")
        print("  ECE002 (Embedded): 10 items (4E/3M/3H)")
        print("All competencies exceed the min_pool_size=10 threshold for adaptive delivery.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
