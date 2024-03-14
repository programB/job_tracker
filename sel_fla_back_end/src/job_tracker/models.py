from marshmallow_sqlalchemy import fields

from job_tracker.database import db
from job_tracker.extensions import ma


# orm model for the tag table
class Tag(db.Model):
    # CREATE TABLE IF NOT EXISTS `tag` (
    #   `tag_id` INT NOT NULL,
    #   `name` VARCHAR(255) NOT NULL,
    #   PRIMARY KEY (`tag_id`)
    # )
    __tablename__ = "tag"
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    # Adding this so LSP doesn't complain
    # about passing arguments when creating new objects.
    # (and it does not expect any).
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class Company(db.Model):
    # CREATE TABLE IF NOT EXISTS `company` (
    #   `company_id` INT(11) NOT NULL AUTO_INCREMENT,
    #   `name` VARCHAR(255) NOT NULL,
    #   `address` VARCHAR(255) NULL DEFAULT NULL,
    #   `town` VARCHAR(255) NULL DEFAULT NULL,
    #   `postalcode` VARCHAR(255) NULL DEFAULT NULL,
    #   `website` VARCHAR(255) NULL DEFAULT NULL,
    #   PRIMARY KEY (`company_id`)
    # )
    __tablename__ = "company"
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    town = db.Column(db.String(255), nullable=True)
    postalcode = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    offers = db.relationship(
        "JobOffer",  # Use this class
        backref="company",
        cascade="all, delete, delete-orphan",  # Del all offers if Company removed
        single_parent=True,  # must be set because: delete-orphan
        order_by="desc(JobOffer.collected)",  # When returning offers sort them
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


# joboffer_tag is an association/junction table.
# CREATE TABLE IF NOT EXISTS `joboffertag` (
#   `joboffer_id` INT NOT NULL,
#   `tag_id` INT NOT NULL,
#   PRIMARY KEY (`joboffer_id`, `tag_id`),
#   INDEX `fk2_idx` (`tag_id` ASC) VISIBLE,
#   CONSTRAINT `fk1` FOREIGN KEY (`joboffer_id`)
#                    REFERENCES `joboffer` (`joboffer_id`),
#   CONSTRAINT `fk2` FOREIGN KEY (`tag_id`)
#                    REFERENCES `tag` (`tag_id`)
# )
# For association/junction tables, the best practice is to use a table
# instead of a database model.
# class JobOfferTag(db.Model):
#     __tablename__ = "joboffertag"
#     joboffer_id = db.Column(db.Integer, db.ForeignKey("joboffer.joboffer_id"))
#     tag_id = db.Column(db.Integer, db.ForeignKey("tag.tag_id"))
joboffer_tag = db.Table(
    "joboffer_tag",
    db.Column("joboffer_id", db.Integer, db.ForeignKey("joboffer.joboffer_id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.tag_id")),
    db.PrimaryKeyConstraint("joboffer_id", "tag_id", name="joboffer_tag_pk"),
)


class JobOffer(db.Model):
    # CREATE TABLE IF NOT EXISTS `joboffer` (
    #   `joboffer_id` INT(11) NOT NULL AUTO_INCREMENT,
    #   `company_id` INT(11) NOT NULL,
    #   `title` VARCHAR(255) NOT NULL,
    #   `posted` DATETIME NOT NULL,
    #   `contracttype` VARCHAR(255) NULL,
    #   `jobmode` VARCHAR(255) NULL,
    #   `joblevel` VARCHAR(255) NULL,
    #   `salary` VARCHAR(255) NULL,
    #   `detailsurl` VARCHAR(255) NULL,
    #   `collected` DATETIME NOT NULL,
    #   PRIMARY KEY (`joboffer_id`),
    #   INDEX `joboffer_FK` (`company_id` ASC) VISIBLE,
    #   CONSTRAINT `joboffer_FK` FOREIGN KEY (`company_id`)
    #                            REFERENCES `company` (`company_id`)
    # )
    __tablename__ = "joboffer"
    joboffer_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.company_id"))
    title = db.Column(db.String(255), nullable=False)
    posted = db.Column(db.DateTime, nullable=False)
    collected = db.Column(db.DateTime, nullable=False)
    contracttype = db.Column(db.String(255), nullable=True)
    jobmode = db.Column(db.String(255), nullable=True)
    joblevel = db.Column(db.String(255), nullable=True)
    salary = db.Column(db.String(255), nullable=True)
    detailsurl = db.Column(db.String(255), nullable=True)  # these tend to be very long
    tags = db.relationship(
        "Tag",  # Use this class
        secondary=joboffer_tag,  # indirect relationship - intermediary: joboffer_tag
        # backref="joboffer",  # this bref. shows in which offers the tag is used
        order_by="asc(Tag.name)",
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


# Declare Models before instantiating Schemas.
# (sqlalchemy.orm.configure_mappers() will run too soon and fail otherwise)


# serializer of the Tag object(s) - converts them to json
class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag
        load_instance = True  # Optional: deserialize to model instances
        sqla_session = db.session
        include_relationships = True


class JobOfferSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = JobOffer
        load_instance = True
        sqla_session = db.session
        include_fk = True
        # 'company_id' will be returned anyway because of include_fk=True
        # so there is no need to follow the relationship and 'company' filed
        include_relationships = False

    # 1. Marshmallow will not follow relationships down the hierarchy
    # (even if include_relationships was set to True)
    # and tags have to be explicitly nested
    # 2. When returning tags we care only about the name not the tag_id
    # tags = fields.Nested(TagSchema, many=True, exclude=("tag_id",))

    # A hack to return a flat list of Tag names (instead of json structure
    # with named fields: name and tag_id) within an offer.
    tags = fields.fields.Pluck(TagSchema, "name", many=True, exclude=("tag_id",))


class CompanySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    offers = fields.Nested(JobOfferSchema, many=True)


class DataPoint(ma.Schema):
    """Used to serialize statistics (datetime, count)
    Warning: Casts datatime to date !
    """

    date = fields.fields.Date()
    count = fields.fields.Integer()


datapoint_schema = DataPoint()
datapoints_schema = DataPoint(many=True)


tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
company_schema = CompanySchema()
joboffer_schema = JobOfferSchema()
joboffers_schema = JobOfferSchema(many=True)
