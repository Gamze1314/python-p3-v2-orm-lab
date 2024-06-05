from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id


    #create properties for year, summay, employee_id
    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self, year):
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError
        

    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, summary):
        if len(summary) > 0:
            self._summary = summary
        else:
            raise ValueError(
                "summary must be a non-empty string"
            )
    
    @property
    def employee_id(self):
        return self._employee_id
    

    @employee_id.setter
    def employee_id(self, employee_id):
        #check if id is in employees table
        if type(employee_id) is int and Employee.find_by_id(employee_id):
            self._employee_id = employee_id
        else:
            raise ValueError(
                "employee_id must reference a employee in the database"
            )

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

#instance method that inserts a new row into the reviews table.
    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""

        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """

        #UPDATE THE OBJECT ID ATTRIBUTE USING PK of NEW ROW.
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
# Update the object id attribute using the primary key value of the new row
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self


    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        review_id = row[1]
        review_instance = cls.all.get(review_id)

        if review_instance:
            #if the instance already exists, set the attributes to row data
            review_instance.year = row[2]
            review_instance.summary = row[3]
            review_instance.employee_id = row[4]
            review_instance.id = row[1]

        else:
        # If the instance doesn't exist, create a new instance and add it to the dictionary
            review_instance = cls(row[1], row[2], row[3], id=review_id)
            cls.all[review_id] = review_instance

        return review_instance


    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = """SELECT * FROM reviews WHERE id = ? LIMIT 1"""

        row = CURSOR.execute(sql, (id, )).fetchone()

        if row:
            return row
        else:
            return None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """UPDATE reviews
            SET year=?, summary=?, employee_id=?
            WHERE id=?
            """
        
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        #commit to db
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""

        if self.id is not None:
        # If the review has a valid ID, proceed with deletion
            sql = "DELETE FROM reviews WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()

        # Remove the object from the dictionary
            if self.id in type(self).all:
                del type(self).all[self.id]

        # Reset the ID attribute to indicate that the object is no longer in the database
            self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = """SELECT * FROM reviews"""

        # cls.new_from_db(row) is being fired off for every row, creates instances for each row.
        return [cls.instance_from_db(row) for row in CURSOR.execute(sql).fetchall()]


