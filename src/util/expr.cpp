/*******************************************************************
 Module: Expression Representation

 Author: Daniel Kroening, kroening@kroening.com

 \*******************************************************************/

#include <cassert>

#include <stack>

#include "string2int.h"
#include "mp_arith.h"
#include "fixedbv.h"
#include "ieee_float.h"
#include "expr.h"
#include "rational.h"
#include "rational_tools.h"
#include "arith_tools.h"
#include "std_expr.h"

#include <iostream> //bat
#include "bv_arithmetic.h" //bat

void copy_expressions(exprt& ex1, const exprt& ex2); //bat
		/*******************************************************************
		 Function: exprt::move_to_operands

		 Inputs:

		 Outputs:

		 Purpose:

		 \*******************************************************************/

void exprt::move_to_operands(exprt &expr) {
	operandst &op = operands();
	op.push_back(static_cast<const exprt &>(get_nil_irep()));
	op.back().swap(expr);
}

/*******************************************************************
 Function: exprt::move_to_operands

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::move_to_operands(exprt &e1, exprt &e2) {
	operandst &op = operands();
#ifndef USE_LIST
	op.reserve(op.size() + 2);
#endif
	op.push_back(static_cast<const exprt &>(get_nil_irep()));
	op.back().swap(e1);
	op.push_back(static_cast<const exprt &>(get_nil_irep()));
	op.back().swap(e2);
}

/*******************************************************************
 Function: exprt::move_to_operands

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::move_to_operands(exprt &e1, exprt &e2, exprt &e3) {
	operandst &op = operands();
#ifndef USE_LIST
	op.reserve(op.size() + 3);
#endif
	op.push_back(static_cast<const exprt &>(get_nil_irep()));
	op.back().swap(e1);
	op.push_back(static_cast<const exprt &>(get_nil_irep()));
	op.back().swap(e2);
	op.push_back(static_cast<const exprt &>(get_nil_irep()));
	op.back().swap(e3);
}

/*******************************************************************
 Function: exprt::copy_to_operands

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::copy_to_operands(const exprt &expr) {
	operands().push_back(expr);
}

/*******************************************************************
 Function: exprt::copy_to_operands

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::copy_to_operands(const exprt &e1, const exprt &e2) {
	operandst &op = operands();
#ifndef USE_LIST
	op.reserve(op.size() + 2);
#endif
	op.push_back(e1);
	op.push_back(e2);
}

/*******************************************************************
 Function: exprt::copy_to_operands

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::copy_to_operands(const exprt &e1, const exprt &e2,
		const exprt &e3) {
	operandst &op = operands();
#ifndef USE_LIST
	op.reserve(op.size() + 3);
#endif
	op.push_back(e1);
	op.push_back(e2);
	op.push_back(e3);
}

/*******************************************************************
 Function: exprt::make_typecast

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::make_typecast(const typet &_type) {
	exprt new_expr(ID_typecast);

	new_expr.move_to_operands(*this);
	new_expr.set(ID_type, _type);

	swap(new_expr);
}

/*******************************************************************
 Function: exprt::make_not

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::make_not() {
	if (is_true()) {
		*this = false_exprt();
		return;
	} else if (is_false()) {
		*this = true_exprt();
		return;
	}

	exprt new_expr;

	if (id() == ID_not && operands().size() == 1) {
		new_expr.swap(operands().front());
	} else {
		new_expr = exprt(ID_not, type());
		new_expr.move_to_operands(*this);
	}

	swap(new_expr);
}

/*******************************************************************
 Function: exprt::is_constant

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::is_constant() const {
	return id() == ID_constant;
}

/*******************************************************************
 Function: exprt::is_true

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::is_true() const {
	return is_constant() && type().id() == ID_bool && get(ID_value) != ID_false;
}

/*******************************************************************
 Function: exprt::is_false

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::is_false() const {
	return is_constant() && type().id() == ID_bool && get(ID_value) == ID_false;
}

/*******************************************************************
 Function: exprt::make_bool

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::make_bool(bool value) {
	*this = exprt(ID_constant, typet(ID_bool));
	set(ID_value, value ? ID_true : ID_false);
}

/*******************************************************************
 Function: exprt::make_true

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::make_true() {
	*this = exprt(ID_constant, typet(ID_bool));
	set(ID_value, ID_true);
}

/*******************************************************************
 Function: exprt::make_false

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::make_false() {
	*this = exprt(ID_constant, typet(ID_bool));
	set(ID_value, ID_false);
}

/*******************************************************************
 Function: operator<

 Inputs:

 Outputs:

 Purpose: defines ordering on expressions for canonicalization

 \*******************************************************************/

bool operator<(const exprt &X, const exprt &Y) {
	return (irept &) X < (irept &) Y;
}

/*******************************************************************
 Function: exprt::negate

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::negate() {
	const irep_idt &type_id = type().id();

	if (type_id == ID_bool)
		make_not();
	else {
		if (is_constant()) {
			const irep_idt &value = get(ID_value);

			if (type_id == ID_integer) {
				set(ID_value,
						integer2string(-string2integer(id2string(value))));
			} else if (type_id == ID_unsignedbv) {
				mp_integer int_value = binary2integer(id2string(value), false);
				typet _type = type();
				*this = from_integer(-int_value, _type);
			} else if (type_id == ID_signedbv) {
				mp_integer int_value = binary2integer(id2string(value), true);
				typet _type = type();
				*this = from_integer(-int_value, _type);
			} else if (type_id == ID_fixedbv) {
				fixedbvt fixedbv_value = fixedbvt(to_constant_expr(*this));
				fixedbv_value.negate();
				*this = fixedbv_value.to_expr();
			} else if (type_id == ID_floatbv) {
				ieee_floatt ieee_float_value = ieee_floatt(
						to_constant_expr(*this));
				ieee_float_value.negate();
				*this = ieee_float_value.to_expr();
			} else {
				make_nil();
				assert(false);
			}
		} else {
			if (id() == ID_unary_minus) {
				exprt tmp;
				assert(operands().size() == 1);
				tmp.swap(op0());
				swap(tmp);
			} else {
				exprt tmp(ID_unary_minus, type());
				tmp.move_to_operands(*this);
				swap(tmp);
			}
		}
	}
}

/*******************************************************************
 Function: exprt::is_boolean

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::is_boolean() const {
	return type().id() == ID_bool;
}

/*******************************************************************
 Function: exprt::is_zero

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::is_zero() const {
	if (is_constant()) {
		const constant_exprt &constant = to_constant_expr(*this);
		const irep_idt &type_id = type().id_string();

		if (type_id == ID_integer || type_id == ID_natural) {
			return constant.value_is_zero_string();
		} else if (type_id == ID_rational) {
			rationalt rat_value;
			if (to_rational(*this, rat_value))
				assert(false);
			return rat_value.is_zero();
		} else if (type_id == ID_unsignedbv || type_id == ID_signedbv) {
			return constant.value_is_zero_string();
		} else if (type_id == ID_fixedbv) {
			if (fixedbvt(constant) == 0)
				return true;
		} else if (type_id == ID_floatbv) {
			if (ieee_floatt(constant) == 0)
				return true;
		} else if (type_id == ID_pointer) {
			return constant.value_is_zero_string();
		}
	}

	return false;
}

/*******************************************************************
 Function: exprt::is_one

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::is_one() const {
	if (is_constant()) {
		const std::string &value = get_string(ID_value);
		const irep_idt &type_id = type().id_string();

		if (type_id == ID_integer || type_id == ID_natural) {
			mp_integer int_value = string2integer(value);
			if (int_value == 1)
				return true;
		} else if (type_id == ID_rational) {
			rationalt rat_value;
			if (to_rational(*this, rat_value))
				assert(false);
			return rat_value.is_one();
		} else if (type_id == ID_unsignedbv || type_id == ID_signedbv) {
			mp_integer int_value = binary2integer(value, false);
			if (int_value == 1)
				return true;
		} else if (type_id == ID_fixedbv) {
			if (fixedbvt(to_constant_expr(*this)) == 1)
				return true;
		} else if (type_id == ID_floatbv) {
			if (ieee_floatt(to_constant_expr(*this)) == 1)
				return true;
		}
	}

	return false;
}

/*******************************************************************
 Function: exprt::sum

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::sum(const exprt &expr) {
	if (!is_constant() || !expr.is_constant())
		return true;
	if (type() != expr.type())
		return true;

	const irep_idt &type_id = type().id();

	if (type_id == ID_integer || type_id == ID_natural) {
		set(ID_value,
				integer2string(
						string2integer(get_string(ID_value))
								+ string2integer(expr.get_string(ID_value))));
		return false;
	} else if (type_id == ID_rational) {
		rationalt a, b;
		if (!to_rational(*this, a) && !to_rational(expr, b)) {
			exprt a_plus_b = from_rational(a + b);
			set(ID_value, a_plus_b.get_string(ID_value));
			return false;
		}
	} else if (type_id == ID_unsignedbv || type_id == ID_signedbv) {
		set(ID_value,
				integer2binary(
						binary2integer(get_string(ID_value), false)
								+ binary2integer(expr.get_string(ID_value),
										false),
						unsafe_string2unsigned(type().get_string(ID_width))));
		return false;
	} else if (type_id == ID_fixedbv) {
		set(ID_value,
				integer2binary(
						binary2integer(get_string(ID_value), false)
								+ binary2integer(expr.get_string(ID_value),
										false),
						unsafe_string2unsigned(type().get_string(ID_width))));
		return false;
	} else if (type_id == ID_floatbv) {
		ieee_floatt f(to_constant_expr(*this));
		f += ieee_floatt(to_constant_expr(expr));
		*this = f.to_expr();
		return false;
	}

	return true;
}

/*******************************************************************
 Function: exprt::mul

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::mul(const exprt &expr) {
	if (!is_constant() || !expr.is_constant())
		return true;
	if (type() != expr.type())
		return true;

	const irep_idt &type_id = type().id();

	if (type_id == ID_integer || type_id == ID_natural) {
		set(ID_value,
				integer2string(
						string2integer(get_string(ID_value))
								* string2integer(expr.get_string(ID_value))));
		return false;
	} else if (type_id == ID_rational) {
		rationalt a, b;
		if (!to_rational(*this, a) && !to_rational(expr, b)) {
			exprt a_mul_b = from_rational(a * b);
			set(ID_value, a_mul_b.get_string(ID_value));
			return false;
		}
	} else if (type_id == ID_unsignedbv || type_id == ID_signedbv) {
		// the following works for signed and unsigned integers
		set(ID_value,
				integer2binary(
						binary2integer(get_string(ID_value), false)
								* binary2integer(expr.get_string(ID_value),
										false),
						unsafe_string2unsigned(type().get_string(ID_width))));
		return false;
	} else if (type_id == ID_fixedbv) {
		fixedbvt f(to_constant_expr(*this));
		f *= fixedbvt(to_constant_expr(expr));
		*this = f.to_expr();
		return false;
	} else if (type_id == ID_floatbv) {
		ieee_floatt f(to_constant_expr(*this));
		f *= ieee_floatt(to_constant_expr(expr));
		*this = f.to_expr();
		return false;
	}

	return true;
}

/*******************************************************************
 Function: exprt::subtract

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

bool exprt::subtract(const exprt &expr) {
	if (!is_constant() || !expr.is_constant())
		return true;

	if (type() != expr.type())
		return true;

	const irep_idt &type_id = type().id();

	if (type_id == ID_integer || type_id == ID_natural) {
		set(ID_value,
				integer2string(
						string2integer(get_string(ID_value))
								- string2integer(expr.get_string(ID_value))));
		return false;
	} else if (type_id == ID_rational) {
		rationalt a, b;
		if (!to_rational(*this, a) && !to_rational(expr, b)) {
			exprt a_minus_b = from_rational(a - b);
			set(ID_value, a_minus_b.get_string(ID_value));
			return false;
		}
	} else if (type_id == ID_unsignedbv || type_id == ID_signedbv) {
		set(ID_value,
				integer2binary(
						binary2integer(get_string(ID_value), false)
								- binary2integer(expr.get_string(ID_value),
										false),
						unsafe_string2unsigned(type().get_string(ID_width))));
		return false;
	}

	return true;
}

/*******************************************************************
 Function: exprt::find_source_location

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

const source_locationt &exprt::find_source_location() const {
	const source_locationt &l = source_location();

	if (l.is_not_nil())
		return l;

	forall_operands(it, (*this)) {
		const source_locationt &l = it->find_source_location();
		if (l.is_not_nil())
			return l;
	}

	return static_cast<const source_locationt &>(get_nil_irep());
}

/*******************************************************************
 Function: exprt::visit

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::visit(expr_visitort &visitor) {
	std::stack<exprt *> stack;

	stack.push(this);

	while (!stack.empty()) {
		exprt &expr = *stack.top();
		stack.pop();

		visitor(expr);

		Forall_operands(it, expr)
			stack.push(&(*it));
	}
}

/*******************************************************************
 Function: exprt::visit

 Inputs:

 Outputs:

 Purpose:

 \*******************************************************************/

void exprt::visit(const_expr_visitort &visitor) const {
	std::stack<const exprt *> stack;

	stack.push(this);

	while (!stack.empty()) {
		const exprt &expr = *stack.top();
		stack.pop();

		visitor(expr);

		forall_operands(it, expr)
			stack.push(&(*it));
	}
}

template void exprt::apply_mutations<
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > > >(
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > >, std::string&) const;
//bat
template<typename OutputIterator>
void exprt::apply_mutations(OutputIterator it, std::string& mutation_level) const {
	//std::cout << "apply mutations begin" << std::endl;
	(*it) = *this; //keep the original expr as the first option
	exprt e = *this; //needed because we can't use apply_mutations_aux directly on (*this) because it's const
	e.apply_mutations_aux(it, e.op1(), mutation_level); //(*this) is always an assignment and we change its RHS (op1)
}

template void exprt::apply_mutations_aux<
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > > >(
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > > it,
		exprt&, std::string& );
//bat
template<typename OutputIterator>
void exprt::apply_mutations_aux(OutputIterator it, exprt& curr, std::string& mutation_level) {
	//std::cout << "apply mutations aux begin. curr is: " << curr << std::endl;

	if (curr.id() == ID_constant) {
		//std::cout << "constant "<<curr.type().id()<< std::endl;
		if (mutation_level=="2"||mutation_level=="3"){
			if (curr.type().id() == "signedbv" || curr.type().id() == "unsignedbv" ) {
				bv_arithmetict cexp(curr);
				mp_integer cvalue = cexp.to_integer();
				//c -> c+1
				cexp.from_integer(cvalue+1);
				curr=cexp.to_expr();
				save_mutated_expr(it);
				//c -> c-1
				cexp.from_integer(cvalue-1);
				curr=cexp.to_expr();
				save_mutated_expr(it);
				//if (mutation_level=="3"){
					//c -> 0
					if (cvalue!=0){
						cexp.from_integer(0);
						curr=cexp.to_expr();
						save_mutated_expr(it);
					}
					//c -> -c
					cexp.from_integer(-cvalue);
					curr=cexp.to_expr();
					save_mutated_expr(it);
				//}
				//restore original value
				cexp.from_integer(cvalue);
				curr=cexp.to_expr();
			}
		}
		return;
	}
	if (curr.id() == ID_symbol || curr.id() == ID_nondet_symbol) {
		//std::cout << "curr is an identifier" << std::endl;
		return;
	}
	this->apply_operator_mutations(it, curr, mutation_level);
	//std::cout << "back from apply operator mutations to apply mutation aux"
			//<< std::endl;

	for (unsigned int i = 0; i < curr.operands().size(); i++) {
		//std::cout << "apply mutation aux before recursive call" << std::endl;
		switch (i) {
		case 0:
			this->apply_mutations_aux(it, curr.op0(), mutation_level);
			break;
		case 1:
			this->apply_mutations_aux(it, curr.op1(), mutation_level);
			break;
		case 2:
			this->apply_mutations_aux(it, curr.op2(), mutation_level);
			break;
		case 3:
			this->apply_mutations_aux(it, curr.op3(), mutation_level);
			break;
		}
		//std::cout << "apply mutation aux returned from recursive call"
				//<< std::endl;
		//std::cout<<"it is: "<< (*it) << std::endl;
	}
}

template void exprt::apply_operator_mutations<
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > > >(
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > >,
		exprt&, std::string&);
//bat
//changes to curr change sub-expr of *this since its a reference
template<typename OutputIterator>
void exprt::apply_operator_mutations(OutputIterator it, exprt& curr,
		std::string& mutation_level) {
	//std::cout<<"apply operator mutations with curr: "<<curr<<std::endl;

	const dstring& old_op = curr.id();
	if (old_op == ID_ge) {
		curr.id(ID_gt); //change >= to >
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_lt); //change >= to <
			save_mutated_expr(it);
			curr.id(ID_le); //change >= to <=
			save_mutated_expr(it);
		}
	} else if (old_op == ID_le) {
		curr.id(ID_lt); //change <= to <
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_gt); //change <= to >
			save_mutated_expr(it);
			curr.id(ID_ge); //change <= to >=
			save_mutated_expr(it);
		}
	} else if (old_op == ID_gt) {
		curr.id(ID_ge); //change > to >=
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_lt); //change > to <
			save_mutated_expr(it);
			curr.id(ID_le); //change > to <=
			save_mutated_expr(it);
		}
	} else if (old_op == ID_lt) {
		curr.id(ID_le); //change < to <=
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_gt); //change < to >
			save_mutated_expr(it);
			curr.id(ID_ge); //change < to >=
			save_mutated_expr(it);
		}
	} else if (old_op == ID_plus) {
		curr.id(ID_minus); //change + to -
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_mult); //change + to *
			save_mutated_expr(it);
			curr.id(ID_div); //change + to /
			save_mutated_expr(it);
			curr.id(ID_mod); //change + to %
			save_mutated_expr(it);
		}
	} else if (old_op == ID_minus) {
		curr.id(ID_plus); //change - to +
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_mult); //change - to *
			save_mutated_expr(it);
			curr.id(ID_div); //change - to /
			save_mutated_expr(it);
			curr.id(ID_mod); //change - to %
			save_mutated_expr(it);
		}
	} else if (old_op == ID_mult) {
		curr.id(ID_div); //change * to /
		save_mutated_expr(it);
		curr.id(ID_mod); //change * to %
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_plus); //change * to +
			save_mutated_expr(it);
			curr.id(ID_minus); //change * to -
			save_mutated_expr(it);
		}
	} else if (old_op == ID_div) {
		curr.id(ID_mod); //change / to %
		save_mutated_expr(it);
		curr.id(ID_mult); //change / to *
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_plus); //change / to +
			save_mutated_expr(it);
			curr.id(ID_minus); //change / to -
			save_mutated_expr(it);
		}
	} else if (old_op == ID_mod) {
		curr.id(ID_div); //change % to /
		save_mutated_expr(it);
		curr.id(ID_mult); //change % to *
		save_mutated_expr(it);
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_plus); //change % to +
			save_mutated_expr(it);
			curr.id(ID_minus); //change % to -
			save_mutated_expr(it);
		}
	} else if (old_op == ID_and) {
		curr.id(ID_or); //change && to ||
		save_mutated_expr(it);
	} else if (old_op == ID_or) {
		curr.id(ID_and); //change || to &&
		save_mutated_expr(it);
	} else if (old_op == ID_equal) {
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_notequal); //change == to !=
			save_mutated_expr(it);
		}
	} else if (old_op == ID_notequal) {
		if (mutation_level=="2"||mutation_level=="3"){
			curr.id(ID_equal); //change != to ==
			save_mutated_expr(it);
		}
	} else if (old_op == ID_bitand) {
		curr.id(ID_bitor); //change & to |
		save_mutated_expr(it);
		curr.id(ID_bitxor); //change & to ^
		save_mutated_expr(it);
	} else if (old_op == ID_bitor) {
		curr.id(ID_bitand); //change | to &
		save_mutated_expr(it);
		curr.id(ID_bitxor); //change | to ^
		save_mutated_expr(it);
	} else if (old_op == ID_bitxor) {
		curr.id(ID_bitand); //change ^ to &
		save_mutated_expr(it);
		curr.id(ID_bitor); //change ^ to |
		save_mutated_expr(it);
	} else if (old_op == ID_shr) {
		curr.id(ID_shl); //change >> to <<
		save_mutated_expr(it);
	} else if (old_op == ID_shl) {
		curr.id(ID_shr); //change << to >>
		save_mutated_expr(it);
	}

	curr.id(old_op); //undo changes to *this
}

template void exprt::save_mutated_expr<
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > > >(
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > >) const;
//bat
template<typename OutputIterator>
void exprt::save_mutated_expr(OutputIterator it) const {
	exprt tmp;
	copy_expressions(tmp, *this);
	it = tmp; //copy changed expression to result vector. equivalent to v.pushback(*this)
}

void copy_expressions(exprt& ex1, const exprt& ex2) {
	//std::cout << " at begin exp1 is: " << ex1 << std::endl;
	//std::cout << " and exp2 is: " << ex2 << std::endl;

	if (ex2.id() == ID_constant || ex2.id() == ID_symbol
			|| ex2.id() == ID_nondet_symbol) {
		ex1 = ex2;
		//std::cout << " after copying exp1 is: " << ex1 << std::endl;
		return;
	}

	ex1 = exprt(ex2.id());
	ex1.type() = ex2.type();
	ex1.operands() = ex2.operands();
	for (unsigned int i = 0; i < ex2.operands().size(); i++) {
		//std::cout<<"here? i="<<i<<" "<<ex2.operands().size()<< std::endl;

		switch (i) {
		case 0: { //std::cout<<"here?????????????????????????"<< std::endl;
			copy_expressions(ex1.op0(), ex2.op0());
			//std::cout<<"now!!!!!!!!!!!!!!!!!!"<< std::endl;
			break;
		}
		case 1: {
			copy_expressions(ex1.op1(), ex2.op1());
			break;
		}
		case 2: {
			copy_expressions(ex1.op2(), ex2.op2());
			break;
		}
		case 3: {
			copy_expressions(ex1.op3(), ex2.op3());
			break;
		}
		}
	}
	//std::cout << " after for exp1 is: " << ex1 << std::endl;
}

template void exprt::replace_operator<
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > > >(
		std::back_insert_iterator<std::vector<exprt, std::allocator<exprt> > > it,
		dstring new_op) const;
//bat
template<typename OutputIterator>
void exprt::replace_operator(OutputIterator it, dstring new_op) const {
	it++; //it is assumed to be pointing to last valid expr
	exprt mutation = *this;
	mutation.op1() = exprt(new_op);
	mutation.op1().type() = this->op1().type();
	mutation.op1().operands() = this->op1().operands();
	//std::cout<<"mutation op0 type "<<mutation.op0().type()<<std::endl;
	//std::cout<<"mutation op1 type "<<mutation.op1().type()<<std::endl;
	//std::cout << "Operator mutation " << mutation << std::endl;
	(*it) = mutation;
}
