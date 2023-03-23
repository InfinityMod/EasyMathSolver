from sympy import Eq
from sympy.utilities.lambdify import lambdify
from sympy.core.function import AppliedUndef


class CalcToolbox:

    @classmethod
    def match_eq(cls, eq0, *eq, deep=True):
        if deep and len(eq) > 1:
            eq = [cls.match_eq(_e, eq[-1]) for _e in eq[:-1]]
        _eq0 = eq0.rhs if hasattr(eq0, "rhs") else eq0

        for _i, _part in enumerate(_eq0.args):
            if isinstance(_part, AppliedUndef):
                for _eq in eq:
                    if type(_part) == type(_eq.lhs):
                        _eq0 = _eq0.subs(_part, _eq.rhs.subs(dict(zip(_eq.lhs.args, _part.args))))
            else:
                _eq0 = _eq0.subs(_part, cls.match_eq(_part, *eq, deep=False))

        if hasattr(eq0, "rhs"):
            _eq0 = Eq(eq0.lhs, _eq0)
        return _eq0
        
       
    @classmethod
    def lambidifyEq(cls, eq):
        _args = eq.lhs.args
        return _args, lambdify(_args, eq.rhs)
