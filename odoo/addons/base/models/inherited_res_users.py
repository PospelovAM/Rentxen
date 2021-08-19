"""
Override the behavior of the res_users.py file
"""
from odoo import fields, models


class InheritedUsers(models.Model):
    """
    Extension for the res.users base model

    new field:
        * partner_my_field - reference to the res.partner model my_field field for easier use inside the view file
    """
    _inherit = 'res.users'

    partner_my_field = fields.Char(compute='_compute_partner_my_field', inverse="_inverse_partner_my_field")

    def _compute_partner_my_field(self):
        """
        Sets the value from partner_id.my_field field
        """
        for user in self:
            user.partner_my_field = user.partner_id.my_field

    def _inverse_partner_my_field(self):
        """
        Sets partner_id.my_field field with the value (allows writing from the res.users model)
        """
        for user in self:
            user.partner_id.my_field = user.partner_my_field

