"""Settings module for test app."""
import os
ENV = "development"
TESTING = True
MAIL_SENDER = 'Records Timeclock <RTimeclock@records.nyc.gov>'
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost:5432/timeclock_test'
SECRET_KEY = "not-so-secret-in-tests"
BCRYPT_LOG_ROUNDS = (
    4
)  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
DEBUG_TB_ENABLED = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WEBPACK_MANIFEST_PATH = "webpack/manifest.json"
WTF_CSRF_ENABLED = False  # Allows form testing
ADMIN = os.environ.get('ADMIN') or 'admin@records.nyc.gov'