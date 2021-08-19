"""
Override the behavior of the res_partner.py file
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InheritedPartner(models.Model):
    """
    Extension for the res.partner base model

    new fields:
        * marginality - increases the cost of products by the specified number of percent
        * my_field - just a useless field
    """

    _inherit = 'res.partner'

    marginality = fields.Integer(string="Marginality", default=0)
    my_field = fields.Char(string="My Field")

    @api.constrains('marginality')
    def _check_marginality(self):
        """Checks if the marginality field is a positive number"""
        for record in self:
            if record.marginality < 0:
                raise ValidationError("The marginality cannot be negative")
