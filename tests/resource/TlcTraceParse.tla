------------ MODULE TlcTraceParse -------------

EXTENDS Naturals, FiniteSets, Sequences, TLC, Reals

VARIABLES
    bool,
    other_bool,
    string_literal,
    json_int,
    list,
    record,
    tuple,
    set,
    map,
    zero_indexed_sequential_map,
    one_indexed_sequential_map,
    string_indexed_map,
    sequence_indexed_map,
    map_indexed_map,
    set_indexed_map,
    negative_number

Init ==
    /\ bool = FALSE
    /\ other_bool = TRUE
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
    /\ sequence_indexed_map =  [ x \in {<<"one", "two">>} |-> 42 ]
    /\ map_indexed_map = [ x \in {[foo |-> 42, bar |-> 42]} |-> 42 ]
    /\ set_indexed_map = [ x \in {{1,2,3},{4,5,6}} |-> 42 ]
    /\ negative_number = -123456

Next ==
    /\ bool' = TRUE
    /\ UNCHANGED other_bool
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
    /\ UNCHANGED sequence_indexed_map
    /\ UNCHANGED map_indexed_map
    /\ UNCHANGED set_indexed_map
    /\ UNCHANGED negative_number

Inv == bool = FALSE

===========================================
