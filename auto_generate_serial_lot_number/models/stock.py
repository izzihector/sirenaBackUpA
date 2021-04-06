# -*- coding utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AutoGenerateLotWizard(models.TransientModel):
    _name = "auto.generate.lot.wizard"

    prepend_text = fields.Char("Prepend Text")
    start_number = fields.Integer("Sequence Start Number", default=0)
    zero_str_size = fields.Integer("Sequence value Characters", default=1)
    append_text = fields.Char("Append Text")
    pro_qty = fields.Integer("Product Lot Quantity", default=1)
    allow_qty = fields.Boolean("Allow Qty")

    def generate_serial_number(self):
        active_ids = self._context.get('active_ids')
        if active_ids:
            stock_move_item = self.env['stock.move'].browse(active_ids[0])
            prepend_text = self.prepend_text or ""
            start_number = self.start_number or 0
            append_text = self.append_text or ""
            pro_qty = self.pro_qty or 1
            zero_str_size = self.zero_str_size or 1
            if pro_qty > stock_move_item.product_uom_qty:
                raise ValidationError("Product Lot Quantity can't be more then Initial Demand")
            if stock_move_item.product_id:
                if stock_move_item.product_id.tracking == 'lot':
                    product_lot_list = []
                    total_qty = stock_move_item.product_uom_qty - stock_move_item.quantity_done
                    while total_qty > 0:
                        lot_name = prepend_text + "" + str(start_number).zfill(zero_str_size) + "" + append_text
                        start_number += 1
                        product_lot_list.append((0, 0, {
                            "lot_name": lot_name,
                            "qty_done": pro_qty if (total_qty - pro_qty) > 0 else total_qty,
                            'company_id': stock_move_item.company_id.id,
                            "product_uom_id": stock_move_item.product_uom.id,
                            "product_id": stock_move_item.product_id.id,
                            'date': stock_move_item.date,
                            'location_id': stock_move_item.location_id.id,
                            'location_dest_id': stock_move_item.location_dest_id.id,
                            'move_id': stock_move_item.id,
                            'state': 'confirmed',
                            'picking_id': stock_move_item.picking_id.id,
                        }))
                        total_qty -= pro_qty
                    if product_lot_list:
                        stock_move_item.move_line_nosuggest_ids = product_lot_list
                if stock_move_item.product_id.tracking == 'serial':
                    product_lot_list = []
                    total_qty = stock_move_item.product_qty - stock_move_item.quantity_done
                    i = 1
                    while total_qty > 0:
                        lot_name = prepend_text + "" + str(start_number).zfill(zero_str_size) + "" + append_text
                        start_number += 1
                        product_lot_list.append((0, 0, {
                            "lot_name": lot_name,
                            'company_id': stock_move_item.company_id,
                            "qty_done": 1,
                            "product_uom_id": stock_move_item.product_uom.id,
                            "product_id": stock_move_item.product_id.id,
                            'date': stock_move_item.date,
                            'location_id': stock_move_item.location_id.id,
                            'location_dest_id': stock_move_item.location_dest_id.id,
                            'move_id': stock_move_item.id,
                            'state': 'confirmed',
                            'picking_id': stock_move_item.picking_id.id,
                        }))
                        total_qty -= i
                    if product_lot_list:
                        stock_move_item.move_line_nosuggest_ids = product_lot_list


class StockPackOperation(models.Model):
    _inherit = "stock.move"

    def auto_genrate_serial2(self):
        new = self.env['auto.generate.lot.wizard'].create({
            'allow_qty': True if self[0].product_id.tracking == 'lot' else False})
        return {
            'name': 'Auto Generate Lot/Serial Number',
            'type': 'ir.actions.act_window',
            'res_model': 'auto.generate.lot.wizard',
            'res_id': new.id,
            'view_id': False,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'flags': {'form': {'action_button': False}, }
        }
