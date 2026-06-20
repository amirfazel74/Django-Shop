import os

settings_path = r"d:\news-site\Django-Shop\eshop_project\settings.py"

with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add apps
apps_to_add = """    'account_module',
    'sms_module',
    'otp_auth',
    'django_ckeditor_5',"""
content = content.replace("    'account_module',", apps_to_add)

# 2. Append settings
append_text = """
customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'outdent', 'underline', 'strikethrough', 'code',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload',
                    'subscript', 'superscript', 'highlight', '|', 'codeBlock',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable', 'alignment', 'sourceEditing',
                    ],

        'image': {
            'toolbar': ['imageTextAlternative', 'imageTitle', '|', 'imageStyle:alignLeft', 'imageStyle:full',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },

        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'alignment': {
            'options': ['left', 'right', 'center', 'justify']
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
            ]
        },

        'language': {
            'ui': 'ar',
            'content': 'ar'
        },
        'direction': {
            'ui': 'rtl',
            'content': 'rtl'
        },
        'rtl': True,
        'contentsLangDirection': 'rtl',
        'htmlSupport': {
            'allow': [
                {'name': 'div', 'attributes': ['dir']},
                {'name': 'span', 'attributes': ['dir']}
            ]
        }
    },
    'fontFamily': {
        'options': [
            'default',
            'Tahoma, Arial, Helvetica, sans-serif',
            'B Nazanin, Nazanin, sans-serif',
            'IRANSans, sans-serif'
        ]

    },
    'htmlSupport': {
        'allow': [
            {'name': 'div', 'attributes': ['dir']},
            {'name': 'span', 'attributes': ['dir']},
            {'name': 'article', 'attributes': True},
            {'name': 'header', 'attributes': True},
            {'name': 'section', 'attributes': True},
            {'name': 'footer', 'attributes': True},
            {'name': 'h4', 'attributes': True},
            {'name': 'h5', 'attributes': True},
            {'name': 'h6', 'attributes': True},
            {'name': 'em', 'attributes': True},
            {'name': 'strong', 'attributes': True},
        ]
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote', 'imageUpload'
        ],
        'toolbar': [
            'heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
            'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock',
            'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageUpload', '|',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
            'insertTable', 'alignment', 'sourceEditing',
        ],
        'alignment': {
            'options': ['left', 'right', 'center', 'justify']
        },
        'image': {
            'toolbar': ['imageTextAlternative', 'imageTitle', '|', 'imageStyle:alignLeft', 'imageStyle:full',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
            ]
        }
    }
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'otp_auth.log',
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'otp_auth': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

LOGIN_URL = '/auth/'
"""

content += append_text

with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Settings restored and LOGIN_URL added.")
