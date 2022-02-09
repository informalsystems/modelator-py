"""Source locations."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/loc.ml>


# type pt_ = { line : int ;
#               bol : int ;
#               col : int ;
#             }
class Pt:
    """Point in string.

    The string is typically the contents of
    a source file.
    """

    def __init__(self, line, bol, col):
        self.line = line
        self.bol = bol  # beginning of line (offset
        # from beginning of file)
        self.col = col  # column number from beginning of line

    # let string_of_pt ?(file="<nofile>") l =
    #   string_of_locus { start = l ; stop = l ; file = file }
    def __str__(self):
        return f"line {self.line}, character {self.col}"

    def __eq__(self, other):
        if other is None:
            return False
        return (
            self.line == other.line and self.bol == other.bol and self.col == other.col
        )

    def __hash__(self):
        return hash(self.offset)

    # let column = function
    #   | Actual l -> l.col
    #   | Dummy -> failwith "Loc.column"
    @property
    def column(self):
        return self.col

    # let offset = function
    #   | Actual l -> l.bol + l.col
    #   | Dummy -> failwith "Loc.offset"
    @property
    def offset(self):
        if self.bol is None or self.col is None:
            raise ValueError("unknown beginning of line or column")
        return self.bol + self.col


# type pt = Actual of pt_ | Dummy

# let dummy = Dummy
# None represents Dummy


# type locus = { start : pt ;
#                stop  : pt ;
#                file : string ;
#              }
class Locus:
    """Location in file."""

    def __init__(self, start, stop, filename):
        self.start = start  # Pt | None
        self.stop = stop  # Pt | None
        self.file = filename

    def __repr__(self):
        return (
            f"{self.file}: "
            f"line {self.start.line}, column {self.start.column} to "
            f"line {self.stop.line}, column {self.stop.column}"
        )

    def __copy__(self):
        return Locus(self.start, self.stop, self.file)

    def __eq__(self, other):
        return (
            self.start == other.start
            and self.stop == other.stop
            and self.file == other.file
        )

    def __hash__(self):
        t = (self.start, self.stop, self.file)
        return hash(t)

    # let left_of l = { l with stop = l.start }
    def left_of(self):
        return Locus(self.start, self.start, self.filename)

    # let right_of l = { l with start = l.stop }
    def right_of(self):
        return Locus(self.stop, self.stop, self.filename)

    # let merge r1 r2 =
    #   if r1.file <> r2.file then
    #     failwith ("Loc.merge: " ^ r1.file ^ " <> " ^ r2.file)
    #   else
    #     try {
    #       start = if offset r1.start <= offset r2.start then
    #                   r1.start else r2.start ;
    #       stop  = if offset r1.stop  >= offset r2.stop  then
    #                   r1.stop  else r2.stop  ;
    #       file = r1.file
    #     } with _ -> unknown
    def merge(self, other):
        if self.file != other.file:
            raise ValueError(f"different files: {self.file}, {other.file}")
        if self.start.offset <= other.start.offset:
            start = self.start
        else:
            start = other.start
        if self.stop.offset >= other.stop.offset:
            stop = self.stop
        else:
            stop = other.stop
        return Locus(start, stop, self.file)


# let unknown = {
#   start = Dummy ;
#   stop  = Dummy ;
#   file  = "<unknown>" ;
# }

unknown = Locus(None, None, "<unknown>")


# let column = function
#   | Actual l -> l.col
#   | Dummy -> failwith "Loc.column"
# NOTE: `column` is implemented above as `Pt.column`


# let line = function
#   | Actual l -> l.line
#   | Dummy -> failwith "Loc.line"
# NOTE: `line` is implemented above as `Pt.line`


# let offset = function
#   | Actual l -> l.bol + l.col
#   | Dummy -> failwith "Loc.offset"
# NOTE: `offset` is implemented above as `Pt.offset`


# let locus_of_position lp =
#   let pt = { line = lp.Lexing.pos_lnum ;
#              bol = lp.Lexing.pos_bol ;
#              col = lp.Lexing.pos_cnum - lp.Lexing.pos_bol + 1 ;
#            }
#   in { start = Actual pt ;
#        stop  = Actual pt ;
#        file  = lp.Lexing.pos_fname ;
#      }
def locus_of_position(filename, lineno, bol, cnum):
    column = cnum - bol + 1  # lp.pos_cnum - lp.pos_bol + 1
    pt = Pt(line=lineno, bol=bol, col=column)  # lp.pos_lnum  # lp.pos_bol,
    return Locus(pt, pt, filename)  # lp.pos_fname


# let merge r1 r2 =
#   if r1.file <> r2.file then
#     failwith ("Loc.merge: " ^ r1.file ^ " <> " ^ r2.file)
#   else
#     try {
#       start = if offset r1.start <= offset r2.start then r1.start else r2.start ;
#       stop  = if offset r1.stop  >= offset r2.stop  then r1.stop  else r2.stop  ;
#       file = r1.file
#     } with _ -> unknown
# NOTE: `merge` is implemented above as `Locus.merge`


# let string_of_locus ?(cap = true) r =
#   let ftok = if cap then "File" else "file" in
#     match r.start, r.stop with
#       | Actual start, Actual stop ->
#           if start.line = stop.line && start.col >= stop.col - 1 then
#             Printf.sprintf "%s %S, line %d, character %d"
#               ftok r.file start.line start.col
#           else
#             (* || start.line <> stop.line
#              * || start.bol <> stop.bol
#              *)
#             if start.line = stop.line then
#               Printf.sprintf "%s %S, line %d, characters %d-%d"
#                 ftok r.file start.line start.col (stop.col - 1)
#             else
#               (* start.line <> stop.line *)
#               Printf.sprintf "%s %S, line %d, character %d to line %d, character %d"
#                 ftok r.file
#                 start.line start.col
#                 stop.line (stop.col - 1)
#       | _ ->
#           Printf.sprintf "%s %S" ftok r.file


# let string_of_locus_nofile r =
#   match r.start, r.stop with
#     | Actual start, Actual stop ->
#         if start.line = stop.line && start.col >= stop.col - 1 then
#           Printf.sprintf "line %d, character %d"
#             start.line start.col
#         else
#           (* || start.line <> stop.line
#            * || start.bol <> stop.bol
#            *)
#           if start.line = stop.line then
#             Printf.sprintf "line %d, characters %d-%d"
#               start.line start.col (stop.col - 1)
#           else
#             (* start.line <> stop.line *)
#             Printf.sprintf "line %d, character %d to line %d, character %d"
#               start.line start.col
#               stop.line (stop.col - 1)
#     | _ -> "<unknown location>"


# let string_of_pt ?(file="<nofile>") l =
#   string_of_locus { start = l ; stop = l ; file = file }
# NOTE: string_of_pt is implemented above as `Pt.__str__`


# let compare r s =
#   match Pervasives.compare (line r.start) (line s.start) with
#     | 0 ->
#         Pervasives.compare (column r.start) (column s.start)
#     | c -> c
