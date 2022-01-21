------------ MODULE TlcMultipleTraceParse -------------

EXTENDS Naturals, FiniteSets, Sequences

VARIABLES
    x,
    y,
    z,
    steps

Init ==
    /\ x = "hello"
    /\ y = 42
    /\ z = [a : 1..2, b : {"foo", "bar"}, c : {<<1, "cat", [dog |-> 3]>>}]
    /\ steps = 0

Next ==
    /\ UNCHANGED x
    /\ UNCHANGED y
    /\ UNCHANGED z
    /\ steps' = IF steps = 8 THEN 0 ELSE steps + 1

Inv == steps < 5

===========================================
