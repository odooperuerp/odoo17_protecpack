{
    'name': 'SMS através de AWS SNS',
    'summary': 'Envío de mensajes de texto através del servicio SNS de AWS',
    'version': '17.0.1.0',
    'website': 'https://www.codlan.com',
    'author': 'Daniel Moreno <daniel@codlan.com>',
    'license': 'OPL-1',
    'depends': ['base','contacts','sms','aws_base'],
    'external_dependencies':{
        'python':['boto3']
    },
    'data': [
        'views/res_config_settings.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'sms_aws_sns/static/src/**/*',
        ]
    },
}
