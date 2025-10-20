{
    "name":"Social Chat Support Buttons",
    "summary": "Add chat support buttons to your website",
    "depends": ["web","website","website_sale"],
    "data":[
        "security/ir_model_access.xml",
        "views/social_chat_support_button.xml",
        "views/res_config_settings.xml",
        "views/frontend_layout.xml"    
    ],
    "assets":{
        "web.assets_frontend":[
            "social_chat_support_button/static/lib/czm-chat-support/czm-chat-support.css",
            "social_chat_support_button/static/lib/prism/prism.css",
            "social_chat_support_button/static/lib/prism/prism.js",
            "social_chat_support_button/static/lib/czm-chat-support/czm-chat-support.min.js",
            "social_chat_support_button/static/src/js/csm-chat-support.js"
        ],
        "web.assets_backend": [
            "social_chat_support_button/static/lib/czm-chat-support/czm-chat-support.css",
            "social_chat_support_button/static/lib/prism/prism.css",
            "social_chat_support_button/static/lib/prism/prism.js",
            "social_chat_support_button/static/lib/czm-chat-support/czm-chat-support.min.js",
            "social_chat_support_button/static/src/components/**/*",
        ],
    }
}