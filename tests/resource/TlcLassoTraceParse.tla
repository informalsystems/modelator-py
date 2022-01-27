------------ MODULE TlcLassoTraceParse -------------

EXTENDS Naturals, FiniteSets, Sequences

VARIABLES
    x

Init == x = 0


Choices ==
    CASE x = 0 -> {1, 3}
    []   x = 1 -> {2}
    []   x = 2 -> {1}
    []   x = 3 -> {4}
    []   x = 4 -> {3}

Next ==
    x' \in Choices

Prop == []<>(x = 5)

Spec == Init /\ [][Next]_x /\ WF_x(Next)

===========================================
