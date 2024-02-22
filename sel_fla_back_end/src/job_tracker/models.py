from job_tracker.database import db


class Tag(db.Model):
    # CREATE TABLE IF NOT EXISTS `tag` (
    #   `tag_id` INT NOT NULL,
    #   `name` VARCHAR(255) NOT NULL,
    #   PRIMARY KEY (`tag_id`)
    # )
    __tablename__ = "tag"
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name


class Company(db.Model):
    # CREATE TABLE IF NOT EXISTS `company` (
    #   `company_id` INT(11) NOT NULL AUTO_INCREMENT,
    #   `name` VARCHAR(45) NOT NULL,
    #   `address` VARCHAR(45) NULL DEFAULT NULL,
    #   `town` VARCHAR(45) NULL DEFAULT NULL,
    #   `postalcode` VARCHAR(45) NULL DEFAULT NULL,
    #   `website` VARCHAR(45) NULL DEFAULT NULL,
    #   PRIMARY KEY (`company_id`)
    # )
    __tablename__ = "company"
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    address = db.Column(db.String(45), nullable=True)
    town = db.Column(db.String(45), nullable=True)
    postalcode = db.Column(db.String(45), nullable=True)
    website = db.Column(db.String(45), nullable=True)
    offers = db.relationship(
        "JobOffer",  # Use this class
        backref="company",
        cascade="all, delete, delete-orphan",  # Del all offers if Company removed
        single_parent=True,  # must be set because: delete-orphan
        order_by="desc(JobOffer.collected)",  # When returning offers sort them
    )

    def __init__(
        self, name, address=None, town=None, postalcode=None, website=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.address = address
        self.town = town
        self.postalcode = postalcode
        self.website = website


# joboffer_tag is an association table.
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
# For association tables, the best practice is to use a table
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
    #   `contracttype` VARCHAR(45) NULL,
    #   `jobmode` VARCHAR(45) NULL,
    #   `joblevel` VARCHAR(45) NULL,
    #   `monthlysalary` INT NULL,
    #   `detailsurl` VARCHAR(45) NULL,
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
    contracttype = db.Column(db.String(45), nullable=True)
    jobmode = db.Column(db.String(45), nullable=True)
    joblevel = db.Column(db.String(45), nullable=True)
    monthlysalary = db.Column(db.Integer, nullable=True)
    detailsurl = db.Column(db.String(45), nullable=True)
    # company = db.relationship("Company", backref="joboffer")
    tags = db.relationship(
        "Tag",  # Use this class
        secondary=joboffer_tag,  # indirect relationship, uses intermediary: joboffer_tag
        backref="joboffer",
    )

    def __init__(
        self,
        title,
        posted,
        collected,
        contracttype=None,
        jobmode=None,
        joblevel=None,
        monthlysalary=None,
        detailsurl=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.posted = posted
        self.collected = collected
        self.contracttype = contracttype
        self.jobmode = jobmode
        self.joblevel = joblevel
        self.monthlysalary = monthlysalary
        self.detailsurl = detailsurl
