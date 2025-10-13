{
    'name':'Configuración de Accesos IAM AWS',
    'author': 'Codlan <hola@codlan.com>',
    'depends': ['base','contacts','sms'],
    'external_dependencies':{
        'python':['boto3']
    },
    'data':[
        'security/groups.xml',
        'views/aws_menu.xml',
        'views/res_config_settings.xml',
    ]
}