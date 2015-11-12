class Config:
    DEBUG = True

class Development(Config):
    STORAGE_BUNDLES = '/tmp/bam_storage_bundles'
    ALLOWED_EXTENSIONS = {'txt', 'mp4', 'png', 'jpg', 'jpeg', 'gif', 'blend', 'zip'}
    SQLALCHEMY_DATABASE_URI = 'sqlite:////db/bam.db'
