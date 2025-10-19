# -*- coding: utf-8 -*-
# class AccountingQueries():
import logging

from itertools import *

_logger=logging.getLogger(__name__)

def query_account_amount_balances(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]
	query_total= """
		select 
			case
			when table_movimientos_periodo.id is not NULL then table_movimientos_periodo.id
			else table_saldos_iniciales.id 
			end id,
			case
			when table_movimientos_periodo.name is not NULL then table_movimientos_periodo.name
			else table_saldos_iniciales.name 
			end,
			case 
			when table_movimientos_periodo.code is not NULL then table_movimientos_periodo.code
			else table_saldos_iniciales.code 
			end code,
			coalesce(table_saldos_iniciales.debit_saldo_inicial,0.00) as debit_saldo_inicial,
			coalesce(table_saldos_iniciales.credit_saldo_inicial,0.00) as credit_saldo_inicial,
			coalesce(table_movimientos_periodo.debit_movimiento_periodo,0.00) as debit_movimiento_periodo,
			coalesce(table_movimientos_periodo.credit_movimiento_periodo,0.00) as credit_movimiento_periodo 
		from
		(select acac.code as code, acac.name as name, acac.id as id, sum(coalesce(aml.debit,0.00)) as debit_saldo_inicial, 
		sum(coalesce(aml.credit,0.00)) as credit_saldo_inicial 
		from
		account_move_line aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		acac.include_initial_balance is True and 
		am.state='posted' and 
		aml.date<'%s' %s 
		group by acac.id
		UNION
		select acac.code as code, acac.name as name, acac.id as id, sum(coalesce(aml.debit,0.00)) as debit_saldo_inicial,
		sum(coalesce(aml.credit,0.00)) as credit_saldo_inicial 
		from
		account_move_line aml join account_account acac on aml.account_id = acac.id join account_move as am on am.id= aml.move_id 
		where
		acac.include_initial_balance is not True and 
		am.state='posted' and 
		aml.date<'%s' and aml.date>='%s' %s
		group by acac.id) as table_saldos_iniciales
		
		full outer join 
		
		(select acac.code as code, acac.name as name, acac.id as id, sum(coalesce(aml.debit,0.00)) as debit_movimiento_periodo,
		sum(coalesce(aml.credit,0.00)) as credit_movimiento_periodo 
		from
		account_move_line aml join
		account_account acac
		on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		am.state='posted' and 
		aml.date>='%s' and aml.date<='%s' %s group by acac.id order by acac.code) as table_movimientos_periodo
		on table_saldos_iniciales.id = table_movimientos_periodo.id
		where
		coalesce(table_saldos_iniciales.debit_saldo_inicial,0.00)>0.00 or 
		coalesce(table_saldos_iniciales.credit_saldo_inicial,0.00)>0.00 or
		coalesce(table_movimientos_periodo.debit_movimiento_periodo,0.00) >0.00 or
		coalesce(table_movimientos_periodo.credit_movimiento_periodo,0.00) >0.00
		order by code """ % (
			fecha_movimiento_debe,
			query_extras,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)
		
	return query_total

######################################################################################################################

def query_account_amount_balances_with_period(fecha_movimiento_debe,fecha_movimiento_haber,init_period_id,query_extras):

	inicio_anio=fecha_movimiento_debe.split('-')[0]

	query_total= """
		select 
			case
			when table_movimientos_periodo.id is not NULL then table_movimientos_periodo.id
			else table_saldos_iniciales.id 
			end id,
			case
			when table_movimientos_periodo.name is not NULL then table_movimientos_periodo.name
			else table_saldos_iniciales.name 
			end,
			case 
			when table_movimientos_periodo.code is not NULL then table_movimientos_periodo.code
			else table_saldos_iniciales.code 
			end code
			,table_saldos_iniciales.debit_saldo_inicial as debit_saldo_inicial ,table_saldos_iniciales.credit_saldo_inicial as
			credit_saldo_inicial,table_movimientos_periodo.debit_movimiento_periodo as debit_movimiento_periodo,
			table_movimientos_periodo.credit_movimiento_periodo as credit_movimiento_periodo 
		from
		(select intermediate.id as id ,intermediate.code as code,intermediate.name as name,
		sum(coalesce(intermediate.debit_saldo_inicial,0.00)) as debit_saldo_inicial,
		sum(coalesce(intermediate.credit_saldo_inicial,0.00)) as credit_saldo_inicial 
		from (
		select acac.code as code,acac.name as name,acac.id as id,
		sum(coalesce(aml.debit,0.00)) as debit_saldo_inicial,
		sum(coalesce(aml.credit,0.00)) as credit_saldo_inicial 
		from
		account_move_line aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		join account_period apfy on apfy.id=aml.period_id 
		where
		am.state='posted' and 
		aml.period_id not in (%s) and 
		aml.date<'%s' and aml.date>='%s' %s
		group by acac.id

		UNION

		select acac.code as code,acac.name as name,acac.id as id,
		sum(coalesce(aml.debit,0.00)) as debit_saldo_inicial,
		sum(coalesce(aml.credit,0.00)) as credit_saldo_inicial 
		from
		account_move_line aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		join account_period apfy on apfy.id=aml.period_id
		where 
		am.state='posted' and 
		aml.period_id in (%s) %s 
		group by acac.id) as intermediate group by id,code,name) as table_saldos_iniciales

		full outer join 

		(select acac.code as code,acac.name as name,acac.id as id,
		sum(coalesce(aml.debit,0.00)) as debit_movimiento_periodo,
		sum(coalesce(aml.credit,0.00)) as credit_movimiento_periodo 
		from
		account_move_line aml join
		account_account acac
		on aml.account_id = acac.id join account_move as am on am.id= aml.move_id join account_period apfy on apfy.id=aml.period_id 
		where
		am.state='posted' and 
		aml.period_id not in (%s) and 
		aml.date>='%s' and aml.date<='%s' %s group by acac.id order by acac.code) as table_movimientos_periodo
		on table_saldos_iniciales.id=table_movimientos_periodo.id order by code """ % (
			init_period_id,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras,
			init_period_id,
			query_extras,
			init_period_id,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)
		
	return query_total


###################################################################################################################
def query_account_amount_balances_group_number_digits(fecha_movimiento_debe,fecha_movimiento_haber,query_extras,number_digits):
	inicio_anio=fecha_movimiento_debe.split('-')[0]
	query = """
			select 
				case
				when table_movimientos_periodo.code is not NULL then table_movimientos_periodo.code
				else table_saldos_iniciales.code 
				end code,
				case
				when table_movimientos_periodo.code is not NULL then 
				(select name from account_group where code_prefix_start = table_movimientos_periodo.code limit 1)
				else (select name from account_group where code_prefix_start = table_saldos_iniciales.code limit 1) 
				end name_code,
				coalesce(table_saldos_iniciales.debit_saldo_inicial,0.00) as debit_saldo_inicial,
				coalesce(table_saldos_iniciales.credit_saldo_inicial,0.00) as credit_saldo_inicial,
				coalesce(table_movimientos_periodo.debit_movimiento_periodo,0.00) as debit_movimiento_periodo,
				coalesce(table_movimientos_periodo.credit_movimiento_periodo,0.00) as credit_movimiento_periodo 

				from
				(
				select 
				substring(acac.code,1,%s) as code,
				sum(coalesce(aml.debit,0.00)) as debit_saldo_inicial, 
				sum(coalesce(aml.credit,0.00)) as credit_saldo_inicial 
				from
				account_move_line aml 
				join account_account acac on aml.account_id = acac.id 
				join account_move as am on am.id= aml.move_id 
				
				where
				acac.include_initial_balance is True and 
				am.state='posted' and 
				aml.date<'%s' %s
				group by substring(acac.code,1,%s)
				
				UNION
				
				select substring(acac.code,1,%s) as code, sum(coalesce(aml.debit,0.00)) as debit_saldo_inicial,
				sum(coalesce(aml.credit,0.00)) as credit_saldo_inicial 
				from
				account_move_line aml 
				join account_account acac on aml.account_id = acac.id 
				join account_move as am on am.id= aml.move_id 

				where
				acac.include_initial_balance is not True and 
				am.state='posted' and 
				aml.date<'%s' and aml.date>='%s' %s
				group by substring(acac.code,1,%s)) as table_saldos_iniciales
				
				full outer join 
				
				(
				select substring(acac.code,1,%s) as code, sum(coalesce(aml.debit,0.00)) as debit_movimiento_periodo,
				sum(coalesce(aml.credit,0.00)) as credit_movimiento_periodo 
				from
				account_move_line aml 
				join account_account acac on aml.account_id = acac.id 
				join account_move as am on am.id= aml.move_id 
				
				where
				am.state='posted' and 
				aml.date>='%s' and aml.date<='%s' %s group by substring(acac.code,1,%s) order by substring(acac.code,1,%s)) as table_movimientos_periodo
				on table_saldos_iniciales.code = table_movimientos_periodo.code
				
				where
				coalesce(table_saldos_iniciales.debit_saldo_inicial,0.00)>0.00 or 
				coalesce(table_saldos_iniciales.credit_saldo_inicial,0.00)>0.00 or
				coalesce(table_movimientos_periodo.debit_movimiento_periodo,0.00) >0.00 or
				coalesce(table_movimientos_periodo.credit_movimiento_periodo,0.00) >0.00
				order by code """%(
					number_digits,
					fecha_movimiento_debe,
					query_extras,
					number_digits,
					number_digits,
					fecha_movimiento_debe,
					"%s-01-01"%(inicio_anio),
					query_extras,
					number_digits,
					number_digits,
					fecha_movimiento_debe,
					fecha_movimiento_haber,
					query_extras,
					number_digits,
					number_digits
					)

	return query

###################################################################################################################

def query_account_amount_balances_opening_balances(fecha_movimiento_debe,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]

	query_total= """
		select 
			acac.code as code, 
			acac.name as name, 
			acac.id as account_id, 
			sum(coalesce(aml.debit,0.00)) as debit_saldo_inicial, 
			sum(coalesce(aml.credit,0.00)) as credit_saldo_inicial, 
			sum(coalesce(aml.debit,0.00) - coalesce(aml.credit,0.00)) as balance_saldo_inicial 
		from account_move_line as aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		acac.include_initial_balance is True and 
		am.state='posted' and 
		aml.date<'%s' %s 
		group by acac.id
		
		UNION
		
		select 
			acac.code as code, 
			acac.name as name, 
			acac.id as account_id, 
			sum(coalesce(aml.debit,0.00)) as debit_saldo_inicial, 
			sum(coalesce(aml.credit,0.00)) as credit_saldo_inicial, 
			sum(coalesce(aml.debit,0.00) - coalesce(aml.credit,0.00)) as balance_saldo_inicial 
		from account_move_line aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		acac.include_initial_balance is not True and 
		am.state='posted' and 
		aml.date<'%s' and aml.date>='%s' %s 
		group by acac.id"""%(
			fecha_movimiento_debe,
			query_extras,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras)

	return query_total


def query_account_amount_balances_opening_balances_ids(fecha_movimiento_debe,query_extras):
	inicio_anio=fecha_movimiento_debe.split('-')[0]

	query_total= """
		select 
		aml.id 
		from account_move_line as aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		acac.include_initial_balance is True and 
		am.state='posted' and 
		aml.date<'%s' %s 
		UNION
		select 
		aml.id 
		from account_move_line aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		acac.include_initial_balance is not True and 
		am.state='posted' and 
		aml.date<'%s' and aml.date>='%s' %s"""%(
			fecha_movimiento_debe,
			query_extras,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras)

	return query_total

######################################################################################################################
def query_account_amount_balances_period_balances_ids(fecha_movimiento_debe,fecha_movimiento_haber,query_extras):

	query_total= """
		select 
			aml.id  
		from account_move_line as aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		am.state='posted' and 
		aml.date>='%s' and aml.date<='%s' %s
		"""%(
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras)

	return query_total


###############################################################################################################################


def query_account_amount_balances_group_account(group_accounts ,fecha_movimiento_debe,fecha_movimiento_haber,query_extras):

	group_accounts_str=""
	accounts = tuple(group_accounts)
	len_accounts = len(accounts or '')
	if len(accounts):
		group_accounts_str = " %s" % (str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

	inicio_anio=fecha_movimiento_debe.split('-')[0]

	query_total= """select 
		acac.code as code,
		acac.id as account_id,
		sum(coalesce(aml.balance,0.00)) as balance

		from account_move_line aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		am.state='posted' and 
		aml.date>='%s' and aml.date<='%s' %s and 
		aml.account_id in %s  
		group by acac.id 
		order by acac.code""" % (
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras,
			group_accounts_str)
		
	return query_total

######################################################################################################
def query_account_amount_balances_with_period_group_account_move_line(group_accounts,fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	group_accounts_str=""
	accounts = tuple(group_accounts)
	len_accounts = len(accounts or '')
	
	if len(accounts):
		group_accounts_str = " %s" % (str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

	inicio_anio=fecha_movimiento_debe.split('-')[0]

	query_total = """
		(select aml.id as aml_id 
		from account_move_line aml 
		join account_move as am on am.id= aml.move_id 
		join account_period apfy on apfy.id=aml.period_id where
		am.state='posted' and 
		aml.period_id not in (select id from account_period where code='00/%s' ) and 
		aml.date<'%s' and aml.date>='%s' %s and
		aml.account_id in %s )
		UNION
		(select aml.id as aml_id
		from account_move_line aml 
		join account_move as am on am.id= aml.move_id 
		join account_period apfy on apfy.id=aml.period_id
		where 
		am.state='posted' and 
		aml.period_id in (select id from account_period where code='00/%s' ) and
		aml.account_id in %s ) 
		UNION 
		(select aml.id as aml_id 
		from account_move_line aml 
		join account_move as am on am.id= aml.move_id 
		join account_period apfy on apfy.id=aml.period_id 
		where
		am.state='posted' and 
		aml.period_id not in (select id from account_period where code='00/%s' ) and 
		aml.date>='%s' and aml.date<='%s' %s and 
		aml.account_id in %s )""" % (
			inicio_anio,
			fecha_movimiento_debe,
			"%s-01-01"%(inicio_anio),
			query_extras,
			group_accounts_str,
			inicio_anio,
			group_accounts_str,
			inicio_anio,
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras,
			group_accounts_str)

	return query_total

############################################################################################
def query_account_amount_balances_group_account_month(group_accounts ,fecha_movimiento_debe,fecha_movimiento_haber,query_extras):

	group_accounts_str=""
	accounts = tuple(group_accounts)
	len_accounts = len(accounts or '')
	if len(accounts):
		group_accounts_str = " %s" % (str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

	inicio_anio=fecha_movimiento_debe.split('-')[0]

	query_total= """select 
		acac.code as code,
		acac.id as account_id,
		extract('YEAR' from aml.date) as year,
		extract('MONTH' from aml.date) as month,
		sum(coalesce(aml.balance,0.00)) as balance
		from account_move_line aml 
		join account_account acac on aml.account_id = acac.id 
		join account_move as am on am.id= aml.move_id 
		where
		am.state='posted' and 
		aml.date>='%s' and 
		aml.date<='%s' %s and 
		aml.account_id in %s  
		group by acac.id,extract('YEAR' from aml.date),extract('MONTH' from aml.date) order by acac.code,year,month """ % (
			fecha_movimiento_debe,
			fecha_movimiento_haber,
			query_extras,
			group_accounts_str)
		
	return query_total


##############################################################################################################

def query_account_amount_balances_with_period_group_account_cum(group_accounts,fecha_movimiento_debe,fecha_movimiento_haber,query_extras):
	group_accounts_str=""
	accounts = tuple(group_accounts)
	len_accounts = len(accounts or '')
	if len(accounts):
		group_accounts_str = " %s" % (str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

	inicio_anio=fecha_movimiento_debe.split('-')[0]
	query_total = """select sum(coalesce(balance,0.00)) as balance 
		from
			((select sum(coalesce(aml.balance,0.00)) as balance 
			from
			account_move_line aml 
			join account_move as am on am.id= aml.move_id 
			where
			am.state='posted' and 
			aml.date<'%s' and aml.date>='%s' %s and
			aml.account_id in %s )
			UNION
			(select sum(coalesce(aml.balance,0.00)) as balance from
			account_move_line aml 
			join account_move as am on am.id= aml.move_id 
			where 
			am.state='posted' and 
			aml.account_id in %s ) 
			UNION 
			(select sum(coalesce(aml.balance,0.00)) as balance from
			account_move_line aml 
			join account_move as am on am.id= aml.move_id  
			where
			am.state='posted' and  
			aml.date>='%s' and aml.date<='%s' %s and 
			aml.account_id in %s )) as table_saldo_accounts""" % (
				fecha_movimiento_debe,
				"%s-01-01"%(inicio_anio),
				query_extras,
				group_accounts_str,
				group_accounts_str,
				fecha_movimiento_debe,
				fecha_movimiento_haber,
				query_extras,
				group_accounts_str)

	return query_total
	#####################################################################

def query_account_group_accounts(prefix_code):
	query_total = ""
	if prefix_code:
		query_total = """
		select
			acac.id,
			acac.code
		from account_account as acac
		where substring(acac.code,1,2) = '%s'
		"""%(prefix_code or '')

	return query_total
