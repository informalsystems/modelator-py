---- MODULE Counter ----
(* A state machine that indefinitely increments a variable. *)
VARIABLE x


Init == x = 0
Next == x' = x + 1
Spec == Init /\ [][Next]_x /\ WF_x(Next)
========================
