------------ MODULE TlcTraceParse -------------

EXTENDS Naturals, FiniteSets, Sequences, TLC, Reals

VARIABLES
    bool,
    string_literal,
    json_int,
    list,
    record,
    tuple,
    set,
    map,
    zero_indexed_sequential_map,
    one_indexed_sequential_map,
    string_indexed_map

Init ==
    /\ bool = FALSE
    /\ string_literal = "hello"
    /\ json_int = 123
    /\ list = <<1,"two">>
    /\ record = [ foo |-> 42, bar |-> 43]
    /\ tuple = <<1,2>>
    /\ set = {1,2,3}
    /\ map = [ x \in 0..5 |-> 42 ] @@ [ x \in {6, 8, 13} |-> "forty-two" ]
    /\ zero_indexed_sequential_map = [ x \in 0..5 |-> 42 ]
    /\ one_indexed_sequential_map = [ x \in 1..5 |-> 42 ]
    /\ string_indexed_map = [ x \in {"one", "two"} |-> 42 ]

Next ==
    /\ bool' = TRUE
    /\ UNCHANGED string_literal
    /\ UNCHANGED json_int
    /\ UNCHANGED list
    /\ UNCHANGED record
    /\ UNCHANGED tuple
    /\ UNCHANGED set
    /\ UNCHANGED map
    /\ UNCHANGED zero_indexed_sequential_map
    /\ UNCHANGED one_indexed_sequential_map
    /\ UNCHANGED string_indexed_map

Inv == bool = FALSE

===========================================
