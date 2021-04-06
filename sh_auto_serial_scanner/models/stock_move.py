# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = ["barcodes.barcode_events_mixin", "stock.move"]

    def sh_auto_serial_scanner_has_tracking(self, barcode):
        if self.picking_code == 'incoming':
            # FOR PURCHASE
            # LOT PRODUCT
            if self.product_id.tracking == 'lot':
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_nosuggest_ids.filtered(
                        lambda r: r.lot_name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            break

                    else:
                        # New Barcode Scan then create new line
                        vals_line = {
                            'product_id': self.product_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'lot_name': barcode,
                            'qty_done': 1,
                            'product_uom_id': self.product_uom.id,
                            'location_id': self.location_id.id,
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(0, 0, vals_line)]
                        })

            # SERIAL PRODUCT
            if self.product_id.tracking == 'serial':
                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == barcode)
                if lines:
                    raise UserError(_("Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Create new line if not found any unallocated serial number line
                    vals_line = {
                        'product_id': self.product_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'lot_name': barcode,
                        'qty_done': 1,
                        'product_uom_id': self.product_uom.id,
                        'location_id': self.location_id.id,
                    }
                    self.update({
                        'move_line_nosuggest_ids': [(0, 0, vals_line)]
                    })
            quantity_done = 0
            for move_line in self.move_line_nosuggest_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if quantity_done == self.product_uom_qty + 1:
                warning_mess = {
                    'title': _('Alert!'),
                    'message': 'Becareful! Quantity exceed than initial demand!'
                }
                return {'warning': warning_mess}

        elif self and self.picking_code in ['outgoing', 'internal']:
            # FOR SALE
            # LOT PRODUCT
            quant_obj = self.env['stock.quant']

            # FOR LOT PRODUCT
            if self.product_id.tracking == 'lot':
                # First Time Scan
                quant = quant_obj.search([
                    ('product_id', '=', self.product_id.id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('lot_id.name', '=', barcode),
                    ('location_id', 'child_of', self.location_id.id)
                ], limit=1)

                if not quant:
                    raise UserError(
                        _("There are no available qty for this lot/serial.%s") % (barcode))

                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_id': quant.lot_id.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            break
                    else:
                        # New Barcode Scan then create new line
                        vals_line = {
                            'product_id': self.product_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'lot_id': quant.lot_id.id,
                            'qty_done': 1,
                            'product_uom_id': self.product_uom.id,
                            'location_id': quant.location_id.id,
                        }
                        self.update({
                            'move_line_ids': [(0, 0, vals_line)]
                        })
            # FOR SERIAL PRODUCT
            if self.product_id.tracking == 'serial':
                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        res = {}
                        if float_compare(line.qty_done, 1.0, precision_rounding=line.product_id.uom_id.rounding) != 0:
                            message = _(
                                'You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name
                            res['warning'] = {'title': _(
                                'Warning'), 'message': message}
                            return res
                        break
                else:
                    list_allocated_serial_ids = []
                    if self.move_line_ids:
                        for line in self.move_line_ids:
                            if line.lot_id:
                                list_allocated_serial_ids.append(
                                    line.lot_id.id)

                    # if need new line.
                    quant = quant_obj.search([
                        ('product_id', '=', self.product_id.id),
                        ('quantity', '>', 0),
                        ('location_id.usage', '=', 'internal'),
                        ('lot_id.name', '=', barcode),
                        ('location_id', 'child_of', self.location_id.id),
                        ('lot_id.id', 'not in', list_allocated_serial_ids),
                    ], limit=1)

                    if not quant:
                        raise UserError(
                            _("There are no available qty for this lot/serial: %s") % (barcode))
                    # New Barcode Scan then create new line
                    vals_line = {
                        'product_id': self.product_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'lot_id': quant.lot_id.id,
                        'qty_done': 1,
                        'product_uom_id': self.product_uom.id,
                        'location_id': quant.location_id.id,
                    }
                    self.update({
                        'move_line_ids': [(0, 0, vals_line)]
                    })

            quantity_done = 0
            for move_line in self._get_move_lines():
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if self.picking_code == 'outgoing' and quantity_done == self.product_uom_qty + 1:
                warning_mess = {
                    'title': _('Alert!'),
                    'message': 'Becareful! Quantity exceed than initial demand!'
                }
                return {'warning': warning_mess}
        else:
            raise UserError(
                _("Picking type is not outgoing or incoming or internal transfer."))

    def sh_auto_serial_scanner_no_tracking(self, barcode):
        move_lines = False

        # INCOMING
        # ===================================
        if self.picking_code in ['incoming']:
            move_lines = self.move_line_nosuggest_ids

        # OUTGOING AND TRANSFER
        # ===================================
        elif self.picking_code in ['outgoing', 'internal']:
            move_lines = self.move_line_ids

        if move_lines:
            for line in move_lines:
                if self.product_id.barcode == barcode:
                    # odoo v14 update below way
                    qty_done = line.qty_done + 1
                    if self.picking_code in ['incoming']:
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, {'qty_done': qty_done})]
                        })
                    if self.picking_code in ['outgoing', 'internal']:
                        self.update({
                            'move_line_ids': [(1, line.id, {'qty_done': qty_done})]
                        })
                    # odoo v14 update below way
                    if self.quantity_done == self.product_uom_qty + 1:
                        warning_mess = {
                            'title': _('Alert!'),
                            'message': 'Becareful! Quantity exceed than initial demand!'
                        }
                        return {'warning': warning_mess}
                    break
                else:
                    raise UserError(
                        _("Scanned Internal Reference/Barcode not exist in any product"))
        else:
            raise UserError(
                _("Pls add all product items in line than rescan."))

    def on_barcode_scanned(self, barcode):
        if self.picking_id.state not in ['confirmed', 'assigned']:
            selections = self.picking_id.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0] ==
                          self.picking_id.state), self.picking_id.state)
            raise UserError(_("You can not scan item in %s state.") % (value))

        res = {}
        if self.has_tracking != 'none':
            res = self.sh_auto_serial_scanner_has_tracking(barcode)
        else:
            res = self.sh_auto_serial_scanner_no_tracking(barcode)
        return res
