{
	'name': 'Distribución analítica masiva',
	'version': "17.0.0.1",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['base','sale','purchase','stock','account'],
	'description':'''
		Distribución analítica masiva en órdenes de venta, compra y movimientos de inventario.
			> Distribución analítica masiva
		''',
	'data':[
		'views/sale_order_view.xml',
		'views/purchase_order_view.xml',
		'views/stock_picking_view.xml',
	],
	'installable': True,
    'auto_install': False,
}