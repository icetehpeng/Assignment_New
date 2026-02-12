"""
Multi-language support system for diverse elderly populations
"""
from typing import Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)

class LanguageManager:
    def __init__(self):
        """Initialize language manager"""
        self.current_language = "en"
        self.supported_languages = ["en", "es", "fr", "de", "zh", "ja", "hi", "pt"]
        
        self.translations = {
            "en": {
                "home": "Home",
                "vital_signs": "Vital Signs",
                "medications": "Medications",
                "activity": "Activity",
                "nutrition": "Nutrition",
                "mood": "Mood & Mental",
                "emergency": "Emergency",
                "geofencing": "Geofencing",
                "smart_home": "Smart Home",
                "caregiver": "Caregiver",
                "voice_control": "Voice Control",
                "privacy": "Privacy",
                "accessibility": "Accessibility",
                "offline_mode": "Offline Mode",
                "reminders": "Reminders",
                "audio_tools": "Audio Tools",
                "intercom": "Intercom",
                "announce": "Announce",
                "chat": "Chat",
                "cctv": "CCTV",
                "logout": "Logout",
                "login": "Login",
                "register": "Register",
                "add": "Add",
                "edit": "Edit",
                "delete": "Delete",
                "save": "Save",
                "cancel": "Cancel",
                "confirm": "Confirm",
                "error": "Error",
                "success": "Success",
                "warning": "Warning",
                "info": "Information",
                "loading": "Loading...",
                "no_data": "No data available",
                "welcome": "Welcome",
                "goodbye": "Goodbye",
            },
            "es": {
                "home": "Inicio",
                "vital_signs": "Signos Vitales",
                "medications": "Medicamentos",
                "activity": "Actividad",
                "nutrition": "Nutrición",
                "mood": "Estado de Ánimo",
                "emergency": "Emergencia",
                "geofencing": "Geovalla",
                "smart_home": "Casa Inteligente",
                "caregiver": "Cuidador",
                "voice_control": "Control de Voz",
                "privacy": "Privacidad",
                "accessibility": "Accesibilidad",
                "offline_mode": "Modo Offline",
                "reminders": "Recordatorios",
                "audio_tools": "Herramientas de Audio",
                "intercom": "Intercomunicador",
                "announce": "Anunciar",
                "chat": "Chat",
                "cctv": "CCTV",
                "logout": "Cerrar Sesión",
                "login": "Iniciar Sesión",
                "register": "Registrarse",
                "add": "Añadir",
                "edit": "Editar",
                "delete": "Eliminar",
                "save": "Guardar",
                "cancel": "Cancelar",
                "confirm": "Confirmar",
                "error": "Error",
                "success": "Éxito",
                "warning": "Advertencia",
                "info": "Información",
                "loading": "Cargando...",
                "no_data": "Sin datos disponibles",
                "welcome": "Bienvenido",
                "goodbye": "Adiós",
            },
            "fr": {
                "home": "Accueil",
                "vital_signs": "Signes Vitaux",
                "medications": "Médicaments",
                "activity": "Activité",
                "nutrition": "Nutrition",
                "mood": "Humeur",
                "emergency": "Urgence",
                "geofencing": "Géofence",
                "smart_home": "Maison Intelligente",
                "caregiver": "Soignant",
                "voice_control": "Contrôle Vocal",
                "privacy": "Confidentialité",
                "accessibility": "Accessibilité",
                "offline_mode": "Mode Hors Ligne",
                "reminders": "Rappels",
                "audio_tools": "Outils Audio",
                "intercom": "Interphone",
                "announce": "Annoncer",
                "chat": "Chat",
                "cctv": "CCTV",
                "logout": "Déconnexion",
                "login": "Connexion",
                "register": "S'inscrire",
                "add": "Ajouter",
                "edit": "Modifier",
                "delete": "Supprimer",
                "save": "Enregistrer",
                "cancel": "Annuler",
                "confirm": "Confirmer",
                "error": "Erreur",
                "success": "Succès",
                "warning": "Avertissement",
                "info": "Information",
                "loading": "Chargement...",
                "no_data": "Aucune donnée disponible",
                "welcome": "Bienvenue",
                "goodbye": "Au revoir",
            },
            "de": {
                "home": "Startseite",
                "vital_signs": "Vitalzeichen",
                "medications": "Medikamente",
                "activity": "Aktivität",
                "nutrition": "Ernährung",
                "mood": "Stimmung",
                "emergency": "Notfall",
                "geofencing": "Geofencing",
                "smart_home": "Intelligentes Zuhause",
                "caregiver": "Betreuer",
                "voice_control": "Sprachsteuerung",
                "privacy": "Datenschutz",
                "accessibility": "Barrierefreiheit",
                "offline_mode": "Offline-Modus",
                "reminders": "Erinnerungen",
                "audio_tools": "Audio-Tools",
                "intercom": "Gegensprechanlage",
                "announce": "Ankündigung",
                "chat": "Chat",
                "cctv": "CCTV",
                "logout": "Abmelden",
                "login": "Anmelden",
                "register": "Registrieren",
                "add": "Hinzufügen",
                "edit": "Bearbeiten",
                "delete": "Löschen",
                "save": "Speichern",
                "cancel": "Abbrechen",
                "confirm": "Bestätigen",
                "error": "Fehler",
                "success": "Erfolg",
                "warning": "Warnung",
                "info": "Information",
                "loading": "Wird geladen...",
                "no_data": "Keine Daten verfügbar",
                "welcome": "Willkommen",
                "goodbye": "Auf Wiedersehen",
            },
            "zh": {
                "home": "主页",
                "vital_signs": "生命体征",
                "medications": "药物",
                "activity": "活动",
                "nutrition": "营养",
                "mood": "心情",
                "emergency": "紧急",
                "geofencing": "地理围栏",
                "smart_home": "智能家居",
                "caregiver": "护理人员",
                "voice_control": "语音控制",
                "privacy": "隐私",
                "accessibility": "无障碍",
                "offline_mode": "离线模式",
                "reminders": "提醒",
                "audio_tools": "音频工具",
                "intercom": "对讲机",
                "announce": "公告",
                "chat": "聊天",
                "cctv": "监控摄像头",
                "logout": "登出",
                "login": "登录",
                "register": "注册",
                "add": "添加",
                "edit": "编辑",
                "delete": "删除",
                "save": "保存",
                "cancel": "取消",
                "confirm": "确认",
                "error": "错误",
                "success": "成功",
                "warning": "警告",
                "info": "信息",
                "loading": "加载中...",
                "no_data": "无可用数据",
                "welcome": "欢迎",
                "goodbye": "再见",
            },
            "ja": {
                "home": "ホーム",
                "vital_signs": "バイタルサイン",
                "medications": "薬物",
                "activity": "活動",
                "nutrition": "栄養",
                "mood": "気分",
                "emergency": "緊急",
                "geofencing": "ジオフェンシング",
                "smart_home": "スマートホーム",
                "caregiver": "介護者",
                "voice_control": "音声制御",
                "privacy": "プライバシー",
                "accessibility": "アクセシビリティ",
                "offline_mode": "オフラインモード",
                "reminders": "リマインダー",
                "audio_tools": "オーディオツール",
                "intercom": "インターホン",
                "announce": "アナウンス",
                "chat": "チャット",
                "cctv": "CCTV",
                "logout": "ログアウト",
                "login": "ログイン",
                "register": "登録",
                "add": "追加",
                "edit": "編集",
                "delete": "削除",
                "save": "保存",
                "cancel": "キャンセル",
                "confirm": "確認",
                "error": "エラー",
                "success": "成功",
                "warning": "警告",
                "info": "情報",
                "loading": "読み込み中...",
                "no_data": "利用可能なデータなし",
                "welcome": "ようこそ",
                "goodbye": "さようなら",
            },
            "hi": {
                "home": "होम",
                "vital_signs": "महत्वपूर्ण संकेत",
                "medications": "दवाएं",
                "activity": "गतिविधि",
                "nutrition": "पोषण",
                "mood": "मनोदशा",
                "emergency": "आपातकाल",
                "geofencing": "भू-बाड़ी",
                "smart_home": "स्मार्ट होम",
                "caregiver": "देखभालकर्ता",
                "voice_control": "वॉयस कंट्रोल",
                "privacy": "गोपनीयता",
                "accessibility": "पहुंच",
                "offline_mode": "ऑफलाइन मोड",
                "reminders": "रिमाइंडर",
                "audio_tools": "ऑडियो उपकरण",
                "intercom": "इंटरकॉम",
                "announce": "घोषणा",
                "chat": "चैट",
                "cctv": "सीसीटीवी",
                "logout": "लॉगआउट",
                "login": "लॉगिन",
                "register": "पंजीकरण",
                "add": "जोड़ें",
                "edit": "संपादित करें",
                "delete": "हटाएं",
                "save": "सहेजें",
                "cancel": "रद्द करें",
                "confirm": "पुष्टि करें",
                "error": "त्रुटि",
                "success": "सफलता",
                "warning": "चेतावनी",
                "info": "जानकारी",
                "loading": "लोड हो रहा है...",
                "no_data": "कोई डेटा उपलब्ध नहीं",
                "welcome": "स्वागत है",
                "goodbye": "अलविदा",
            },
            "pt": {
                "home": "Início",
                "vital_signs": "Sinais Vitais",
                "medications": "Medicamentos",
                "activity": "Atividade",
                "nutrition": "Nutrição",
                "mood": "Humor",
                "emergency": "Emergência",
                "geofencing": "Geofencing",
                "smart_home": "Casa Inteligente",
                "caregiver": "Cuidador",
                "voice_control": "Controle de Voz",
                "privacy": "Privacidade",
                "accessibility": "Acessibilidade",
                "offline_mode": "Modo Offline",
                "reminders": "Lembretes",
                "audio_tools": "Ferramentas de Áudio",
                "intercom": "Intercomunicador",
                "announce": "Anunciar",
                "chat": "Chat",
                "cctv": "CCTV",
                "logout": "Sair",
                "login": "Entrar",
                "register": "Registrar",
                "add": "Adicionar",
                "edit": "Editar",
                "delete": "Excluir",
                "save": "Salvar",
                "cancel": "Cancelar",
                "confirm": "Confirmar",
                "error": "Erro",
                "success": "Sucesso",
                "warning": "Aviso",
                "info": "Informação",
                "loading": "Carregando...",
                "no_data": "Nenhum dado disponível",
                "welcome": "Bem-vindo",
                "goodbye": "Adeus",
            }
        }
    
    def set_language(self, language_code: str) -> bool:
        """Set current language"""
        if language_code in self.supported_languages:
            self.current_language = language_code
            logger.info(f"Language changed to {language_code}")
            return True
        logger.warning(f"Language {language_code} not supported")
        return False
    
    def get_text(self, key: str, language: Optional[str] = None) -> str:
        """Get translated text"""
        lang = language or self.current_language
        if lang not in self.translations:
            lang = "en"
        
        return self.translations[lang].get(key, key)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        language_names = {
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "zh": "中文",
            "ja": "日本語",
            "hi": "हिन्दी",
            "pt": "Português"
        }
        return {code: language_names.get(code, code) for code in self.supported_languages}
    
    def save_language_preference(self, username: str, language: str, db_conn=None) -> bool:
        """Save user's language preference"""
        if db_conn:
            try:
                cursor = db_conn.cursor()
                cursor.execute("""
                    INSERT INTO user_preferences (username, language, updated_at)
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE language=%s, updated_at=NOW()
                """, (username, language, language))
                db_conn.commit()
                logger.info(f"Language preference saved for {username}: {language}")
                return True
            except Exception as e:
                logger.error(f"Error saving language preference: {e}")
        return False
    
    def load_language_preference(self, username: str, db_conn=None) -> str:
        """Load user's saved language preference"""
        if db_conn:
            try:
                cursor = db_conn.cursor()
                cursor.execute("SELECT language FROM user_preferences WHERE username=%s", (username,))
                result = cursor.fetchone()
                if result and result[0]:
                    return result[0]
            except Exception as e:
                logger.error(f"Error loading language preference: {e}")
        return "en"  # Default to English
