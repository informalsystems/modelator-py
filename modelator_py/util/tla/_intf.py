"""This module describes an abstract interface.

The implementation is in the module `tla.tokens`.
"""
# Copyright 2020 by California Institute of Technology
# Copyright (C) 2008-2010  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/pars/intf.ml>


# # (** Tokens *)
# # module type Tok = sig
# #   type token
# #     (** Type of tokens *)


# class Token:
#     """Type of tokens."""

#     pass


# #   val bof : Loc.locus -> token  (* beginning of file *)
# #     (** token representing start of file *)


# def bof(locus):
#     """Token representing beginning of file."""
#     return token


# #   val rep : token -> string
# #     (** String representation of tokens *)


# def rep(token):
#     """String representation of token."""
#     return string


# #   val locus : token -> Loc.locus
# #     (** Origin of the token *)


# def locus(token):
#     """Location of the token in text."""
#     return locus


# #   val eq : token -> token -> bool
# #     (** Are the tokens equivalent? *)


# def eq(token, other_token):
#     """Whether tokens are equivalent."""
#     return boolean


# #   val pp_print_token : Format.formatter -> token -> unit
# #     (** For use in format strings *)


# def pp_print_token(formatter, token):
#     """For use in format strings."""
#     pass


# # end

# # (** Precedence *)
# # module type Prec = sig
# #   type prec
# #     (** Abstract type of precedence *)


# class Prec:
#     """Abstract type of operator precedence."""

#     pass


# #   val below : prec -> prec -> bool
# #     (** {!below} [p q] means that [p] is entirely below [q] *)


# def below(prec, other_prec):
#     """Whether `prec` is entirely below `other_prec`."""
#     return boolean


# #   val conflict : prec -> prec -> bool
# #     (** {!conflict} [p q] means that an unbracketed expression with
# #         two operators of precedence [p] and [q] respectively would be
# #         ambiguous. *)


# def conflict(prec, other_prec):
#     """Whether `prec` and `other_prec` have overlapping precedence ranges."""
#     return boolean


# # end
