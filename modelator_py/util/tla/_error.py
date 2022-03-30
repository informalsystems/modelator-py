"""Parser error messages."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/pars/error.ml>
#
#
# open Ext


def setdefault(value, default):
    if value is None:
        value = default
    return value


# type error_ =
#     { err_unex : string option ;
#       err_exps : string list ;
#       err_msgs : string list ;
#       err_ints : string list }
class Error_:
    def __init__(self, err_unex=None, err_exps=None, err_msgs=None, err_ints=None):
        self.err_unex = err_unex
        self.err_exps = setdefault(err_exps, list())
        self.err_msgs = setdefault(err_msgs, list())
        self.err_ints = setdefault(err_ints, list())


# type error = Error of error_ * Loc.locus
class Error:
    def __init__(self, error_, locus):
        self.error_ = error_
        self.locus = locus


# type t = error
class T(Error):
    pass


# (* FIXME make this return a string *)
# let print_error ?(verbose = false) ouch (Error (err, locus)) =
#   let unexp =
#     match err.err_unex with
#       | None -> ""
#       | Some s -> "Unexpected " ^ s ^ "\n"
#   in
#   let exps =
#     match List.unique (err.err_exps) with
#       | [] -> ""
#       | exps ->
#           "Expecting one of {" ^ String.concat ", " exps ^ "}\n"
#   in
#   let ints =
#     if verbose then
#       String.concat "" (List.map
#                           (fun i -> "[Internal] " ^ i ^ "\n")
#                           (List.unique err.err_ints))
#     else ""
#   in
#   let msgs =
#     String.concat "" (List.map
#                         (fun i -> i ^ "\n")
#                         (List.unique (err.err_msgs)))
#   in
#   let loc = Printf.sprintf "%s\n" (Loc.string_of_locus locus) in
#   output_string ouch loc;
#   output_string ouch unexp ;
#   output_string ouch exps ;
#   output_string ouch msgs ;
#   output_string ouch ints ;
#   flush ouch;
#
#   if !Params.toolbox
#   then Toolbox_msg.print_warning (loc ^ unexp ^ exps ^ msgs ^ ints);
# ;;
def print_error(verbose, ouch, error):
    if error.error_.err_unex is None:
        unexp = ""
    else:
        unexp = f"Unexpected {error.error_.err_unex}\n"
    if not error.error_.err_exps:
        exps = ""
    else:
        exps = "Expecting one of:  {s}\n".format(s="\n".join(error.error_.err_exps))
    if verbose:
        ints = "".join(f"[Internal] {i}\n" for i in error.error_.err_ints)
    else:
        ints = ""
    msgs = "".join(i + "\n" for i in error.error_.err_msgs)
    print(error.locus)
    print(unexp)
    print(exps)
    print(msgs)
    print(ints)


# let error locus =
#   Error ({ err_unex = None ;
#            err_exps = [] ;
#            err_ints = [] ;
#            err_msgs = [] }, locus)
def error(locus):
    return Error(Error_(), locus)


# let err_combine (Error (a, alocus)) (Error (b, blocus)) =
#   let combo a b =
#     { err_unex = None ;
#       err_exps = a.err_exps @ b.err_exps ;
#       err_ints = a.err_ints @ b.err_ints ;
#       err_msgs = a.err_msgs @ b.err_msgs ;
#     }
#   in
#     Error (combo a b, blocus)
def err_combine(a, b):
    error_ = Error_(
        err_unex=None,
        err_exps=a.error_.err_exps + b.error_.err_exps,
        err_ints=a.error_.err_ints + b.error_.err_ints,
        err_msgs=a.error_.err_msgs + b.error_.err_msgs,
    )
    return Error(error_, b.locus)


# let err_add_message msg (Error (e, elocus)) =
#   Error ({ e with err_msgs = msg :: e.err_msgs }, elocus)
def err_add_message(msg, error):
    e = error.error_
    elocus = error.locus
    error_ = Error_(
        err_unex=e.err_unex,
        err_exps=e.err_exps,
        err_msgs=[msg] + e.err_msgs,
        err_ints=e.err_ints,
    )
    return Error(error_, elocus)


# let err_add_internal i (Error (e, elocus)) =
#   Error ({ e with err_ints = i :: e.err_ints }, elocus)
def err_add_internal(i, error):
    e = error.error_
    elocus = error.locus
    error_ = Error_(
        err_unex=e.err_unex,
        err_exps=e.err_exps,
        err_msgs=e.err_msgs,
        err_ints=[i] + e.err_ints,
    )
    return Error(error_, elocus)


# let err_add_expecting x (Error (e, elocus)) =
#   Error ({ e with err_exps = x :: e.err_exps }, elocus)
def err_add_expecting(x, error):
    e = error.error_
    elocus = error.locus
    error_ = Error_(
        err_unex=e.err_unex,
        err_exps=[x] + e.err_exps,
        err_msgs=e.err_msgs,
        err_ints=e.err_ints,
    )
    return Error(error_, elocus)


# let err_set_unexpected u (Error (e, elocus)) =
#   Error ({ e with err_unex = Some u }, elocus)
def err_set_unexpected(u, error):
    e = error.error_
    elocus = error.locus
    error_ = Error_(
        err_unex=u, err_exps=e.err_exps, err_msgs=e.err_msgs, err_ints=e.err_ints
    )
    return Error(error_, elocus)
