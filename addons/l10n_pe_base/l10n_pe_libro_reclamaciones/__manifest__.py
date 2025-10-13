{
    'name': 'Libro de reclamaciones',
    'depends': ['base','base_setup','base_automation','mail','sale','web','website'],
    'data': [
        'security/security.xml',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'data/automation.xml',
        'views/views.xml',
        'views/res_config_settings.xml',
        'report/libro_reclamaciones_template.xml',
        'report/report.xml',
        'templates/libro_reclamaciones.xml',
     ],
    "assets": {
        "web.assets_frontend": [
            "l10n_pe_libro_reclamaciones/static/src/js/libro_reclamacion.js",
        ]
    }
}
