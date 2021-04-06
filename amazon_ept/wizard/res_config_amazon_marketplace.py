# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
Added class for configure the amazon marketplace and also added fields to configure marketplace
details.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AmazonMarketplaceConfig(models.TransientModel):
    """
    Added class to config the amazon marketplace
    """
    _name = 'res.config.amazon.marketplace'
    _description = 'Amazon Marketplace Configurations'

    # def _domain_marketplace(self):
    #     ids = self.on_change_seller_id()
    #     return [('marketplace_ids', 'in', ids)]
    #
    # def _domain_is_pan(self):
    #     active_seller = self._context.get('default_seller_id')
    #     amazon_active_seller = self.env['amazon.seller.ept'].browse(active_seller)
    #     if amazon_active_seller.is_pan_european:
    #         return amazon_active_seller.is_pan_european

    @api.depends('seller_id')
    def _compute_is_mkt_created_via_program(self):
        if self.seller_id.instance_ids and self.seller_id.amazon_program:
            self.is_mkt_created_via_program = True
        else:
            self.is_mkt_created_via_program = False

    marketplace_ids = fields.Many2many('amazon.marketplace.ept',
                                       'res_config_amazon_marketplace_rel',
                                       'res_marketplace_id', 'amazon_market_place_id',
                                       string="Marketplaces",
                                       help="List of Amazon Marketplaces.")

    pan_eu_marketplace_ids = fields.Many2many('amazon.marketplace.ept',
                                              'res_config_amazon_marketplace_pan_eu_rel',
                                              'res_pan_eu_marketplace_id',
                                              'amazon_market_place_id', string="PAN EU Marketplace")

    efn_marketplace_ids = fields.Many2many('amazon.marketplace.ept',
                                           'res_config_amazon_markeplace_efn_rel',
                                           'res_efn_marketplace_id', 'amazon_market_place_id',
                                           string="EFN Marketplace"
                                           )
    mci_marketplace_ids = fields.Many2many('amazon.marketplace.ept',
                                           'res_config_amazon_marketplace_mci_rel',
                                           'res_mci_marketplace_id', 'amazon_market_place_id',
                                           string="MCI Marketplace")
    cep_marketplace_ids = fields.Many2many('amazon.marketplace.ept',
                                           'res_config_amazon_marketplace_cep_rel',
                                           'res_cep_markeplace_id', 'amazon_marke_place_id',
                                           string="CEP Markeplace")
    mci_efn_marketplace_ids = fields.Many2many('amazon.marketplace.ept',
                                               'res_config_amazon_markeplace_efn_mci_rel',
                                               'res_efn_mci_marketplace_id',
                                               'amazon_market_place_id',
                                               string="EFN+MCI Marketplace")

    seller_id = fields.Many2one('amazon.seller.ept', string='Seller',
                                help="Select Amazon Seller Name listed in odoo")
    is_mkt_created_via_program = fields.Boolean('Is MKT created ?',
                                                compute='_compute_is_mkt_created_via_program')
    is_european_region = fields.Boolean('Is European Region ?', compute='_compute_region',
                                        default=False)

    is_pan_european_program_activated = fields.Boolean('Is Pan European Program Activated ?',
                                                       help="Enable it if Pan European Program is "
                                                            "activated from seller central account")

    other_pan_europe_country = fields.Many2many('res.country', 'other_pan_europe_country_rel',
                                                'res_marketplace_id',
                                                'country_id', "Other Pan Europe Countries")

    amazon_program = fields.Selection([('pan_eu', 'PAN EU'),
                                       ('efn', 'EFN'),
                                       ('mci', 'MCI'),
                                       ('cep', 'CEP'),
                                       ('efn+mci', 'EFN+MCI')],
                                      help="PAN EU: Pan European Program"
                                           "EFN: European Fulfillment Network"
                                           "MCI: Multi Country Inventory"
                                           "CEP: Central European Program"
                                           "EFN + MCI: Joint Functionality of EFN and MCI")

    store_inv_wh_efn = fields.Many2one('res.country', string="Store Inv. Country")
    store_inv_wh_cep = fields.Many2many('res.country', 'res_config_mkt_country_rel',
                                        'res_cep_mkt_id', 'country_id',
                                        string="Store Inv. Country for CEP")

    store_inv_wh_mci = fields.Many2many('res.country', 'res_config_mkt_country_mci_rel',
                                        'res_mci_mkt_id', 'country_id',
                                        string="Store Inv. Country for MCI")

    store_inv_wh_mci_efn = fields.Many2many('res.country', 'res_config_mkt_country_mci_efn_rel',
                                            'res_mci_efn_mkt_id', 'country_id',
                                            string="Store Inv. Country for MCI+EFN")
    amazon_selling = fields.Selection([('FBA', 'FBA'),
                                       ('FBM', 'FBM'),
                                       ('Both', 'FBA & FBM')])

    @api.depends('seller_id')
    def _compute_region(self):
        is_european = self.seller_id.marketplace_ids.filtered( \
            lambda x: x.market_place_id in ['A2VIGQ35RCS4UG', 'A1PA6795UKMFR9', 'ARBP9OOSHTCHU',
                                            'A1RKKUPIHCS9HS', 'A13V1IB3VIYZZH', 'A1F83G8C2ARO7P',
                                            'A21TJRUUN4KGV', 'APJ6JRA9NG5V4', 'A17E79C6D8DWNP',
                                            'A1805IZSGTT6HS', 'A33AVAJ2PDY3EV', 'A2NODRKZP88ZB9'])
        if is_european:
            self.is_european_region = True
        else:
            self.is_european_region = False

    def already_created_mkt(self, seller_id):
        """
        Find already created Marketplaces
        :param seller_id: amazon.seller.ept()
        :return: amazon.marketplace.ept()
        """
        market_place_id = seller_id.instance_ids.filtered( \
            lambda x: x.market_place_id).mapped('market_place_id')
        marketplace_id = seller_id.marketplace_ids.filtered( \
            lambda x: x.market_place_id not in market_place_id and x.country_id.code != 'SE')
        return marketplace_id

    @api.onchange('amazon_selling')
    def _onchange_amazon_selling(self):
        """
        Method for on change of Amazon selling.
        @author: Maulik Barad on Date 01-Feb-2020.
        """
        if not self.amazon_selling or self.amazon_selling == "FBM":
            self.amazon_program = False
        else:
            self.amazon_program = self.seller_id.amazon_program

    @api.onchange('amazon_program')
    def _onchange_amazon_program(self):
        """
        based on amazon program will update the marketplace_ids
        """
        market_place_obj = self.env['amazon.marketplace.ept']
        if self.amazon_program == 'pan_eu':
            marketplace_ids = self.seller_id.marketplace_ids.filtered \
                (lambda x: x.market_place_id in ['A13V1IB3VIYZZH', 'A1F83G8C2ARO7P',
                                                 'A1RKKUPIHCS9HS', 'APJ6JRA9NG5V4',
                                                 'A1805IZSGTT6HS', 'A1PA6795UKMFR9',
                                                 'A2NODRKZP88ZB9'])
            self.pan_eu_marketplace_ids = marketplace_ids.ids
        if self.amazon_program == 'cep':
            countries = self.env['res.country'].search([('code', 'in', ['DE', 'PL', 'CZ'])])
            self.store_inv_wh_cep = countries.ids
            marketplace_id = self.already_created_mkt(self.seller_id)
            return {'domain': {'cep_marketplace_ids': [('id', 'in', marketplace_id.ids)]}}
        if self.amazon_program == 'mci':
            marketplace_id = self.already_created_mkt(self.seller_id)
            countries = self.seller_id.amz_warehouse_ids.partner_id.mapped('country_id')
            inv_store_country = self.env['res.country'].search( \
                [('code', 'in', ['DE', 'IT', 'FR', 'ES',
                                 'GB', 'CZ', 'PL']), ('id', 'not in', countries.ids)])
            return {'domain': {'mci_marketplace_ids': [('id', 'in', marketplace_id.ids)],
                               'store_inv_wh_mci': [('id', 'in', inv_store_country.ids)]}}
        if self.amazon_program == 'efn':
            marketplace_id = self.already_created_mkt(self.seller_id)
            return {'domain': {'efn_marketplace_ids': [('id', 'in', marketplace_id.ids)]}}
        if self.amazon_program == 'efn+mci':
            marketplace_id = self.already_created_mkt(self.seller_id)
            countries = self.seller_id.amz_warehouse_ids.partner_id.mapped('country_id')
            inv_store_country = self.env['res.country'].search( \
                [('code', 'in', ['DE', 'IT', 'FR', 'ES', 'GB', 'CZ', 'PL']),
                 ('id', 'not in', countries.ids)])
            seller_country = self.seller_id.country_id
            seller_local_mkt = market_place_obj.search([('seller_id', '=', self.seller_id.id),
                                                        ('country_id', '=', seller_country.id)])
            self.store_inv_wh_mci_efn = seller_country.ids
            self.mci_efn_marketplace_ids = seller_local_mkt.ids
            return {'domain': {'mci_efn_marketplace_ids': [('id', 'in', marketplace_id.ids)],
                               'store_inv_wh_mci_efn': [('id', 'in', inv_store_country.ids)]}}

    @api.onchange('seller_id')
    def _onchange_seller_id(self):
        """
        Based on seller it will display the amazon_selling, amazon_program.
        also return the other_pan_europe_country is amazon program in 'pan_eu'
        and store_inv_wh_efn if amazon program in efn
        """
        marketplace_id = self._context.get('deactivate_marketplace')
        self.amazon_selling = self.seller_id.amazon_selling
        amazon_program = self.seller_id.amazon_program
        self.amazon_program = amazon_program
        if (not self.is_european_region) or (self.seller_id.amazon_selling == 'FBM'):
            return {'domain': {'marketplace_ids': [('id', 'in', marketplace_id)]}}

        if amazon_program == 'pan_eu':
            self.other_pan_europe_country = self.seller_id.other_pan_europe_country_ids.ids
        if amazon_program == 'efn':
            self.store_inv_wh_efn = self.seller_id.store_inv_wh_efn.id

    def prepare_amazon_marketplace_vals(self, marketplace, warehouse_id):
        """
        Prepare dictionary for amazon marketplace instance
        :param marketplace: amazon.marketplace.ept()
        :param warehouse_id: warehouse record.
        :return: vals {}
        """
        res_lang_obj = self.env['res.lang']
        company_id = self.seller_id.company_id
        lang_id = res_lang_obj.search([('code', '=', self._context.get('lang'))])
        if not lang_id:
            lang_id = res_lang_obj.search([('active', '=', True)], limit=1)
        vals = {
            'name': marketplace.name,
            'marketplace_id': marketplace.id,
            'seller_id': self.seller_id.id,
            'warehouse_id': warehouse_id,
            'company_id': company_id.id,
            'ending_balance_description': 'Transfer to Bank',
            'lang_id': lang_id.id,
        }
        vals = self.create_or_set_journal_and_pricelist(marketplace, vals)
        return vals

    def search_fbm_warehouse(self, company_id):
        """
        Search amazon warehouse from odoo warehouses.
        :param company_id:
        :return:
        """
        warehouse_obj = self.env['stock.warehouse']
        default_warehouse = self.sudo().env.ref('stock.warehouse0')
        if default_warehouse.active:
            if self.seller_id.company_id == default_warehouse.company_id:
                warehouse_id = default_warehouse.id
            else:
                warehouse = warehouse_obj.search(
                    [('company_id', '=', company_id.id), ('is_fba_warehouse', '=', False)], limit=1)
                warehouse_id = warehouse.id
        else:
            warehouse = warehouse_obj.search(
                [('company_id', '=', company_id.id), ('is_fba_warehouse', '=', False)])
            if warehouse:
                warehouse_id = warehouse[0].id
            else:
                raise UserError(_('Warehouse not found for %s Company. Create a New Warehouse' % (
                    company_id.name)))

        return warehouse_id

    def prepare_journal_vals(self, marketplace, code):
        """
        This  method will prepare the journal values
        """
        journal_vals = {
            'name': marketplace.name + "(%s)" % self.seller_id.name,
            'type': 'bank',
            'code': code,
            'currency_id': (marketplace.currency_id or marketplace.country_id.currency_id).id,
            'company_id': self.seller_id.company_id.id
        }
        return journal_vals

    def prepare_pricelist_vals(self, marketplace):
        """
        This method will prepare the price_list values
        :param marketplace : marketplace record.
        """
        pricelist_vals = {
            'name': marketplace.name + " Pricelist(%s)" % self.seller_id.name,
            'discount_policy': 'with_discount',
            'company_id': self.seller_id.company_id.id,
            'currency_id': (marketplace.currency_id or marketplace.country_id.currency_id).id,
        }
        return pricelist_vals

    def create_or_set_journal_and_pricelist(self, marketplace, vals):
        """
        This method will create or set journal an pricelist and update the vals dict.
        param vals: marketplace vals
        return : dict
        """
        account_journal_obj = self.env['account.journal']
        account_obj = self.env['account.account']
        product_pricelist_obj = self.env['product.pricelist']
        if marketplace.name.find('.') != -1:
            name = marketplace.name.rsplit('.', 1)
            code = name[1]
        else:
            code = marketplace.name
        code = "%s%s" % (self.seller_id.name[0:3], code[0:2])
        journal_id = account_journal_obj.search(
            [('code', '=', code[0:5]), ('company_id', '=', self.seller_id.company_id.id),
             ('currency_id', '=',
              (marketplace.currency_id or marketplace.country_id.currency_id).id)])
        if journal_id:
            vals.update({'settlement_report_journal_id': journal_id.id})
        else:
            journal_vals = self.prepare_journal_vals(marketplace, code[0:5])
            settlement_journal_id = account_journal_obj.create(
                journal_vals)
            if not settlement_journal_id.currency_id.active:
                settlement_journal_id.currency_id.active = True
            vals.update(
                {'settlement_report_journal_id': settlement_journal_id.id})

        ending_balance = account_obj.search(
            [('company_id', '=', self.seller_id.company_id.id), ('reconcile', '=', True), (
                'user_type_id.id', '=',
                self.env.ref('account.data_account_type_current_assets').id),
             ('deprecated', '=', False)], limit=1)
        vals.update({'ending_balance_account_id': ending_balance.id})

        pricelist_vals = self.prepare_pricelist_vals(marketplace)

        pricelist_id = product_pricelist_obj.create(pricelist_vals)
        vals.update({'pricelist_id': pricelist_id.id})
        return vals

    def create_view_type_location(self):
        """
        This method will create view type location dict
        """
        loc_vals = {'name': self.seller_id.name,
                    'usage': 'view',
                    'company_id': self.seller_id.company_id.id,
                    'location_id': self.env.ref('stock.stock_location_locations').id
                    }
        return loc_vals

    def create_internal_type_location(self, view_location_id):
        """
        This method will prepare an vals to create an internal type location
        """
        lot_loc_vals = {'name': 'Stock',
                        'active': True,
                        'usage': 'internal',
                        'company_id': self.seller_id.company_id.id,
                        'location_id': view_location_id}
        return lot_loc_vals

    def get_fba_warehouse(self, view_location_id, lot_stock_id, marketplace, unsellable_location,
                          country=False):
        amazon_fulfillment_code_obj = self.env['amazon.fulfillment.country.rel']
        stock_warehouse_obj = self.env['stock.warehouse']
        partner_obj = self.env['res.partner']

        if marketplace:
            if marketplace.name.find('.') != -1:
                name = marketplace.name.rsplit('.', 1)
                code = name[1]
            else:
                code = marketplace.name
        else:
            code = country.code
        code = "%s%s" % (code, self.seller_id.id)
        partner_vals = {'name': code, \
                        'country_id': country.id if country else False}
        partner = partner_obj.create(partner_vals)
        vals = {'name': 'FBA %s(%s)' % (
            marketplace and marketplace.name or country.name, self.seller_id.name),
                'is_fba_warehouse': True,
                'code': code[0:5],
                'company_id': self.seller_id.company_id.id,
                'seller_id': self.seller_id.id,
                'unsellable_location_id': unsellable_location and unsellable_location.id or False,
                'partner_id': partner and partner.id or False
                }
        fba_warehouse_id = stock_warehouse_obj.create(vals)
        location_id = fba_warehouse_id.lot_stock_id
        if view_location_id and lot_stock_id:
            fba_warehouse_id.write(
                {'view_location_id': view_location_id, 'lot_stock_id': lot_stock_id})
            fba_warehouse_id.route_ids.mapped('rule_ids').filtered( \
                lambda l: l.location_src_id.id == location_id.id).write( \
                {'location_src_id': lot_stock_id})
        amazon_fulfillment_code_obj.load_fulfillment_code( \
            marketplace and marketplace.country_id or country,
            self.seller_id.id,
            fba_warehouse_id.id)

        return fba_warehouse_id

    def get_location_for_pan_eu(self):
        """
        This method will find the view location and lot stock id.
        """
        stock_location_obj = self.env['stock.location']
        if self._context.get('switch_fulfillment'):
            loc_vals = self.create_view_type_location()
            view_location_id = stock_location_obj.create(loc_vals).id
            lot_loc_vals = self.create_internal_type_location(view_location_id)
            lot_stock_id = stock_location_obj.create(lot_loc_vals).id
        else:
            instance_found = self.seller_id.instance_ids.filtered( \
                lambda l: l.fba_warehouse_id != False)
            if not instance_found:
                loc_vals = self.create_view_type_location()
                view_location_id = stock_location_obj.create(loc_vals).id
                lot_loc_vals = self.create_internal_type_location(view_location_id)
                lot_stock_id = stock_location_obj.create(lot_loc_vals).id
            else:
                view_location_id = instance_found[0].fba_warehouse_id.view_location_id.id
                lot_stock_id = instance_found[0].fba_warehouse_id.lot_stock_id.id

        return view_location_id, lot_stock_id

    def create_unsellable_location(self):
        """
        This method will find or create the unsellable location
        """
        stock_location_obj = self.env['stock.location']
        unsellable_location = stock_location_obj.search(
            [('name', '=', self.seller_id.name + " Unsellable"),
             ('usage', '=', 'internal'),
             ('company_id', '=', self.seller_id.company_id.id)])
        if not unsellable_location:
            unsellable_vals = {
                'name': self.seller_id.name + " Unsellable",
                'usage': 'internal',
                'company_id': self.seller_id.company_id.id
            }
            unsellable_location = stock_location_obj.create(unsellable_vals)
        return unsellable_location

    def switch_amazon_fulfillment_by(self):
        """
        This method is used to set the FBA warehouse, selling on , amazon program and other
        details in seller.
        """
        amazon_instance_obj = self.env['amazon.instance.ept']
        if self.amazon_selling == self.seller_id.amazon_selling:
            raise UserError(_('Selected fulfillment is already set in seller.'))

        if self.amazon_selling != 'FBM':
            if not self.seller_id.is_european_region:
                for instance in self.seller_id.instance_ids:
                    marketplace = instance.marketplace_id
                    view_location_id, lot_stock_id = False, False
                    warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
                    unsellable_location = self.create_unsellable_location()
                    vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                    fba_warehouse_id = self.get_fba_warehouse(view_location_id, lot_stock_id, \
                                                              marketplace, unsellable_location,
                                                              marketplace.country_id)
                    vals.update({'fba_warehouse_id': fba_warehouse_id.id})
                    fba_warehouse_id.write({'resupply_wh_ids': [warehouse_id]})
                    instance.write({'fba_warehouse_id': fba_warehouse_id.id})
                for marketplace in self.marketplace_ids:
                    view_location_id, lot_stock_id = False, False
                    warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
                    unsellable_location = self.create_unsellable_location()
                    vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                    fba_warehouse_id = self.get_fba_warehouse(view_location_id, lot_stock_id,
                                                              marketplace, unsellable_location,
                                                              marketplace.country_id)
                    vals.update({'fba_warehouse_id': fba_warehouse_id.id})
                    fba_warehouse_id.write({'resupply_wh_ids': [warehouse_id]})
                    amazon_instance_obj.create(vals)

                self.seller_id.write({'amazon_selling': self.amazon_selling})

            if self.amazon_program == 'pan_eu':
                warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
                marketplace_ids = self.pan_eu_marketplace_ids
                nl_vals = {}
                unsellable_location = self.create_unsellable_location()
                view_location_id, lot_stock_id = self.with_context({
                    'switch_fulfillment': True}).get_location_for_pan_eu()
                for marketplace in marketplace_ids:
                    instance_exist = self.seller_id.instance_ids.filtered(
                        lambda x: x.marketplace_id.id == marketplace.id)
                    if instance_exist:
                        if marketplace.market_place_id not in ['A1805IZSGTT6HS']:
                            fba_warehouse_id = self.get_fba_warehouse(view_location_id, \
                                                                      lot_stock_id, marketplace,
                                                                      unsellable_location, \
                                                                      marketplace.country_id)
                            instance_exist.write({'fba_warehouse_id': fba_warehouse_id.id})
                            fba_warehouse_id.write({'resupply_wh_ids': [warehouse_id]})
                            continue
                    vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                    if marketplace.market_place_id not in ['A1805IZSGTT6HS']:
                        fba_warehouse_id = self.get_fba_warehouse(view_location_id, lot_stock_id, \
                                                                  marketplace, unsellable_location, \
                                                                  marketplace.country_id)
                    else:
                        # Set Germany instance warehouse as FBA warehouse for NL Instance
                        nl_vals = vals
                        continue
                    vals.update({'fba_warehouse_id': fba_warehouse_id.id})
                    fba_warehouse_id.write({'resupply_wh_ids': [warehouse_id]})
                    amazon_instance_obj.create(vals)
                if nl_vals:
                    de_warehouse_id = self.seller_id.instance_ids.filtered( \
                        lambda
                            x: x.marketplace_id.market_place_id == 'A1PA6795UKMFR9').fba_warehouse_id
                    if de_warehouse_id:
                        nl_vals.update({'fba_warehouse_id': de_warehouse_id.id})
                    amazon_instance_obj.create(nl_vals)
                self.seller_id.write({
                    'other_pan_europe_country_ids': [(6, 0, self.other_pan_europe_country.ids)],
                    'is_european_region': self.is_european_region,
                    'amazon_program': self.amazon_program,
                    'amazon_selling': self.amazon_selling
                })
                resupply_wh = self.seller_id.amz_warehouse_ids.filtered( \
                    lambda r: r.partner_id.country_id.id == self.seller_id.country_id.id)
                resupply_wh and resupply_wh.write({'resupply_wh_ids': [warehouse_id]})
                if self.other_pan_europe_country:
                    for country in self.other_pan_europe_country:
                        if self.seller_id.amz_warehouse_ids.filtered( \
                                lambda l: l.partner_id.country_id.id == country.id):
                            continue
                        self.get_fba_warehouse(view_location_id, lot_stock_id, False,
                                               unsellable_location, country)

            elif self.amazon_program == 'efn':
                if self.store_inv_wh_efn:
                    warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
                    unsellable_location = self.create_unsellable_location()
                    fba_warehouse = self.seller_id.amz_warehouse_ids.filtered( \
                        lambda
                            r: r.is_fba_warehouse and r.partner_id.country_id.id == self.store_inv_wh_efn.id)
                    if not fba_warehouse:
                        fba_warehouse = self.get_fba_warehouse(False, False, False,
                                                               unsellable_location,
                                                               self.store_inv_wh_efn)
                    for marketplace in self.efn_marketplace_ids:
                        instance_exist = self.seller_id.instance_ids.filtered(
                            lambda x: x.marketplace_id.id == marketplace.id)
                        if instance_exist:
                            instance_exist.write({'fba_warehouse_id': fba_warehouse.id})
                            continue
                        vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                        vals.update({'fba_warehouse_id': fba_warehouse.id})
                        amazon_instance_obj.create(vals)
                    self.seller_id.write({'store_inv_wh_efn': self.store_inv_wh_efn.id,
                                          'amazon_program': self.amazon_program,
                                          'is_european_region': self.is_european_region,
                                          'amazon_selling': self.amazon_selling})
                    resupply_wh = self.seller_id.amz_warehouse_ids.filtered( \
                        lambda r: r.partner_id.country_id.id == self.store_inv_wh_efn.id)

                    if resupply_wh and warehouse_id:
                        resupply_wh.write({'resupply_wh_ids': [warehouse_id]})

            elif self.amazon_program == 'mci':
                warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
                unsellable_location = self.create_unsellable_location()
                for inv_store_wh in self.store_inv_wh_mci:
                    fba_warehouse = self.seller_id.amz_warehouse_ids.filtered( \
                        lambda
                            r: r.is_fba_warehouse and r.partner_id.country_id.id == inv_store_wh.id)
                    if not fba_warehouse:
                        fba_warehouse = self.get_fba_warehouse(False, False, False,
                                                               unsellable_location, inv_store_wh)
                    fba_warehouse.write({'resupply_wh_ids': [warehouse_id]})
                for marketplace in self.mci_marketplace_ids:
                    instance_exist = self.seller_id.instance_ids.filtered( \
                        lambda x: x.marketplace_id.id == marketplace.id)
                    wh_for_mkt = self.seller_id.amz_warehouse_ids.filtered( \
                        lambda
                            r: r.is_fba_warehouse and r.partner_id.country_id.id == marketplace.country_id.id)
                    if not wh_for_mkt:
                        wh_for_mkt = self.seller_id.amz_warehouse_ids.filtered( \
                            lambda
                                r: r.is_fba_warehouse and r.partner_id.country_id.id == self.seller_id.country_id.id)
                    if instance_exist:
                        instance_exist.write({'fba_warehouse_id': wh_for_mkt.id})
                        continue

                    vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                    wh_for_mkt and vals.update({'fba_warehouse_id': wh_for_mkt.id})
                    amazon_instance_obj.create(vals)
                self.seller_id.write({'amazon_program': self.amazon_program,
                                      'is_european_region': self.is_european_region,
                                      'amazon_selling': self.amazon_selling})

            elif self.amazon_program == 'cep':
                warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
                unsellable_location = self.create_unsellable_location()
                de_country = self.store_inv_wh_cep.filtered(lambda r: r.code == 'DE')
                de_fba_wh = self.seller_id.amz_warehouse_ids.filtered( \
                    lambda r: r.is_fba_warehouse and r.partner_id.country_id.code == 'DE')
                if not de_fba_wh:
                    de_fba_wh = self.get_fba_warehouse(False, False, False,
                                                       unsellable_location, de_country)
                de_fba_wh.write({'resupply_wh_ids': [warehouse_id]})
                view_location_id = de_fba_wh.view_location_id.id
                lot_stock_id = de_fba_wh.lot_stock_id.id
                for store_inv in self.store_inv_wh_cep.filtered(lambda r: r.code in ('CZ', 'PL')):
                    fba_warehouse = self.seller_id.amz_warehouse_ids.filtered( \
                        lambda r: r.is_fba_warehouse and r.partner_id.country_id.id == store_inv.id)
                    if not fba_warehouse:
                        fba_warehouse = self.get_fba_warehouse(view_location_id, lot_stock_id,
                                                               False, unsellable_location,
                                                               store_inv)

                for marketplace in self.cep_marketplace_ids:
                    instance_exist = self.seller_id.instance_ids.filtered( \
                        lambda x: x.marketplace_id.id == marketplace.id)
                    if instance_exist:
                        continue
                    vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                    amazon_instance_obj.create(vals)
                self.seller_id.instance_ids.write({'fba_warehouse_id': de_fba_wh.id})
                self.seller_id.write({'amazon_program': self.amazon_program,
                                      'is_european_region': self.is_european_region,
                                      'amazon_selling': self.amazon_selling})

            elif self.amazon_program == 'efn+mci':
                warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
                unsellable_location = self.create_unsellable_location()
                for inv_store_wh in self.store_inv_wh_mci_efn:
                    fba_warehouse = self.seller_id.amz_warehouse_ids.filtered( \
                        lambda
                            r: r.is_fba_warehouse and r.partner_id.country_id.id == inv_store_wh.id)
                    if not fba_warehouse:
                        fba_warehouse = self.get_fba_warehouse(False, False, False,
                                                               unsellable_location, inv_store_wh)
                    fba_warehouse.write({'resupply_wh_ids': [warehouse_id]})
                for marketplace in self.mci_efn_marketplace_ids:
                    instance_exist = self.seller_id.instance_ids.filtered( \
                        lambda x: x.marketplace_id.id == marketplace.id)
                    if instance_exist:
                        wh_for_mkt = self.seller_id.amz_warehouse_ids.filtered( \
                            lambda
                                r: r.is_fba_warehouse and r.partner_id.country_id.id == marketplace.country_id.id)
                        if not wh_for_mkt:
                            wh_for_mkt = self.seller_id.amz_warehouse_ids.filtered( \
                                lambda
                                    r: r.is_fba_warehouse and r.partner_id.country_id.id == self.seller_id.country_id.id)
                        instance_exist.write({'fba_warehouse_id': wh_for_mkt.id})
                        continue
                    vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                    wh_for_mkt = self.seller_id.amz_warehouse_ids.filtered( \
                        lambda
                            r: r.is_fba_warehouse and r.partner_id.country_id.id == self.seller_id.country_id.id)
                    wh_for_mkt and vals.update({'fba_warehouse_id': wh_for_mkt.id})
                    amazon_instance_obj.create(vals)
                self.seller_id.write({'amazon_program': self.amazon_program,
                                      'is_european_region': self.is_european_region,
                                      'amazon_selling': self.amazon_selling})
        else:
            self.seller_id.deactivate_fba_warehouse()
            self.seller_id.instance_ids.write({"fba_warehouse_id": False})

            warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
            for marketplace in self.marketplace_ids:
                instance_exist = self.seller_id.instance_ids.filtered(
                    lambda x: x.marketplace_id.id == marketplace.id)
                if instance_exist:
                    continue
                vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                amazon_instance_obj.create(vals)
            self.seller_id.write({'amazon_program': self.amazon_program,
                                  'is_european_region': self.is_european_region,
                                  'amazon_selling': self.amazon_selling})
        return True

    def create_amazon_marketplace(self):
        """
        Create Amazon Marketplace instance in ERP
        :return: True
        """
        if self._context.get('switch_fulfillment'):
            self.switch_amazon_fulfillment_by()
            return True
        amazon_instances = []
        amazon_instance_obj = self.env['amazon.instance.ept']
        if not self.amazon_program:
            warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
            view_location_id, lot_stock_id = False, False
            for marketplace in self.marketplace_ids:
                instance_exist = self.seller_id.instance_ids.filtered(
                    lambda x: x.marketplace_id.id == marketplace.id)
                if instance_exist:
                    raise UserError(_(
                        'Instance already exist for %s with given Credential.' % (
                            marketplace.name)))
                vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                if self.amazon_selling != 'FBM':
                    unsellable_location = self.create_unsellable_location()
                    fba_warehouse_id = self.get_fba_warehouse(view_location_id, lot_stock_id,
                                                              marketplace, unsellable_location,
                                                              marketplace.country_id)

                    vals.update({'fba_warehouse_id': fba_warehouse_id.id})
                    if fba_warehouse_id:
                        fba_warehouse_id.write({'resupply_wh_ids': warehouse.ids})
                instance = amazon_instance_obj.create(vals)
                amazon_instances.append(instance)
            self.seller_id.write({'is_european_region': self.is_european_region})

        elif self.amazon_program == 'pan_eu':
            nl_vals = {}
            unsellable_location = self.create_unsellable_location()
            warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
            view_location_id, lot_stock_id = self.get_location_for_pan_eu()
            for marketplace in self.pan_eu_marketplace_ids:
                instance_exist = self.seller_id.instance_ids.filtered(
                    lambda x: x.marketplace_id.id == marketplace.id)
                if instance_exist:
                    continue
                vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                # Skip Creating FBA Warehouse for NL Marketplace
                if marketplace.market_place_id not in ['A1805IZSGTT6HS']:
                    fba_warehouse_id = self.get_fba_warehouse(view_location_id, lot_stock_id,
                                                              marketplace, unsellable_location,
                                                              marketplace.country_id)
                    vals.update({'fba_warehouse_id': fba_warehouse_id.id})
                else:
                    # Set Germany instance warehouse as FBA warehouse for NL Instance
                    nl_vals = vals
                    continue
                instance = amazon_instance_obj.create(vals)
                amazon_instances.append(instance)
            if nl_vals:
                de_warehouse_id = self.seller_id.instance_ids.filtered( \
                    lambda x: x.marketplace_id.market_place_id == 'A1PA6795UKMFR9').fba_warehouse_id
                if de_warehouse_id:
                    nl_vals.update({'fba_warehouse_id': de_warehouse_id.id})
                instance = amazon_instance_obj.create(nl_vals)
                amazon_instances.append(instance)
            self.seller_id.write({
                'other_pan_europe_country_ids': [(6, 0, self.other_pan_europe_country.ids)],
                'is_european_region': self.is_european_region,
                'amazon_program': self.amazon_program})
            resupply_wh = self.seller_id.amz_warehouse_ids.filtered( \
                lambda r: r.partner_id.country_id.id == self.seller_id.country_id.id)
            resupply_wh and resupply_wh.write({'resupply_wh_ids': warehouse.ids})
            if self.other_pan_europe_country:
                for country in self.other_pan_europe_country:
                    if self.seller_id.amz_warehouse_ids.filtered( \
                            lambda l: l.partner_id.country_id.id == country.id):
                        continue
                    self.get_fba_warehouse(view_location_id, lot_stock_id, False,
                                           unsellable_location, country)
        elif self.amazon_program == 'efn':
            if self.seller_id.store_inv_wh_efn:
                if self.seller_id.store_inv_wh_efn.id != self.store_inv_wh_efn.id:
                    raise UserError(_( \
                        'You can not change the inventory store location , If you want to change '
                        'it please first inactive the seller and create a new seller.'))
            unsellable_location = self.create_unsellable_location()
            view_location_id, lot_stock_id = False, False
            warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
            fba_warehouse = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                lambda
                    r: r.is_fba_warehouse and r.partner_id.country_id.id == self.store_inv_wh_efn.id)
            if not fba_warehouse:
                fba_warehouse = self.get_fba_warehouse(view_location_id, lot_stock_id, False,
                                                       unsellable_location, self.store_inv_wh_efn)

            for marketplace in self.efn_marketplace_ids:
                instance_exist = self.seller_id.instance_ids.filtered( \
                    lambda x: x.marketplace_id.id == marketplace.id)
                if instance_exist:
                    raise UserError(_( \
                        'Instance already exist for %s with given Credential.' % ( \
                            marketplace.name)))
                vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                vals.update({'fba_warehouse_id': fba_warehouse.id})
                instance = amazon_instance_obj.create(vals)
                amazon_instances.append(instance)
            self.seller_id.write({'store_inv_wh_efn': self.store_inv_wh_efn.id,
                                  'amazon_program': self.amazon_program,
                                  'is_european_region': self.is_european_region})
            resupply_wh = self.seller_id.amz_warehouse_ids.filtered(
                lambda r: r.partner_id.country_id.id == self.store_inv_wh_efn.id)
            if resupply_wh and warehouse_id:
                warehouse = self.env['stock.warehouse'].browse(warehouse_id)
                resupply_wh and resupply_wh.write({'resupply_wh_ids': warehouse.ids})
        elif self.amazon_program == 'mci':
            unsellable_location = self.create_unsellable_location()
            view_location_id, lot_stock_id = False, False
            warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
            for inv_store_wh in self.store_inv_wh_mci:
                fba_warehouse = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                    lambda r: r.is_fba_warehouse and r.partner_id.country_id.id == inv_store_wh.id)
                if not fba_warehouse:
                    fba_warehouse = self.get_fba_warehouse( \
                        view_location_id, lot_stock_id, False, unsellable_location, inv_store_wh)
                fba_warehouse.write({'resupply_wh_ids': warehouse.ids})
            for marketplace in self.mci_marketplace_ids:
                instance_exist = self.seller_id.instance_ids.filtered( \
                    lambda x: x.marketplace_id.id == marketplace.id)
                if instance_exist:
                    raise UserError(_('Instance already exist for %s with given Credential.' % ( \
                        marketplace.name)))
                wh_for_mkt = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                    lambda
                        r: r.is_fba_warehouse and r.partner_id.country_id.id == marketplace.country_id.id)
                if not wh_for_mkt:
                    wh_for_mkt = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                        lambda
                            r: r.is_fba_warehouse and r.partner_id.country_id.id == self.seller_id.country_id.id)
                vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                if marketplace.market_place_id in ['A1805IZSGTT6HS']:
                    de_fba_wh = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                        lambda r: r.is_fba_warehouse and r.partner_id.country_id.code == 'DE')
                    wh_for_mkt = de_fba_wh if de_fba_wh else wh_for_mkt
                wh_for_mkt and vals.update({'fba_warehouse_id': wh_for_mkt.id})
                instance = amazon_instance_obj.create(vals)
                amazon_instances.append(instance)

            self.seller_id.write({'amazon_program': self.amazon_program,
                                  'is_european_region': self.is_european_region})
        elif self.amazon_program == 'cep':
            unsellable_location = self.create_unsellable_location()
            view_location_id, lot_stock_id = False, False
            warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
            de_country = self.store_inv_wh_cep.filtered(lambda r: r.code == 'DE')
            de_fba_wh = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                lambda r: r.is_fba_warehouse and r.partner_id.country_id.code == 'DE')
            if not de_fba_wh:
                de_fba_wh = self.get_fba_warehouse(view_location_id, lot_stock_id, False,
                                                   unsellable_location, de_country)
            de_fba_wh.write({'resupply_wh_ids': warehouse.ids})
            view_location_id = de_fba_wh.view_location_id.id
            lot_stock_id = de_fba_wh.lot_stock_id.id
            for store_inv in self.store_inv_wh_cep.filtered(lambda r: r.code in ('CZ', 'PL')):
                fba_warehouse = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                    lambda r: r.is_fba_warehouse and r.partner_id.country_id.id == store_inv.id)
                if not fba_warehouse:
                    fba_warehouse = self.get_fba_warehouse(view_location_id, lot_stock_id, False,
                                                           unsellable_location, store_inv)

            for marketplace in self.cep_marketplace_ids:
                instance_exist = self.seller_id.instance_ids.filtered(
                    lambda x: x.marketplace_id.id == marketplace.id)
                if instance_exist:
                    raise UserError(_(
                        'Instance already exist for %s with given Credential.' % (
                            marketplace.name)))

                vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                vals.update({'fba_warehouse_id': de_fba_wh.id})
                instance = amazon_instance_obj.create(vals)
                amazon_instances.append(instance)
            self.seller_id.write({'amazon_program': self.amazon_program,
                                  'is_european_region': self.is_european_region})
        elif self.amazon_program == 'efn+mci':
            unsellable_location = self.create_unsellable_location()
            view_location_id, lot_stock_id = False, False
            warehouse_id = self.search_fbm_warehouse(self.seller_id.company_id)
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
            for inv_store_wh in self.store_inv_wh_mci_efn:
                fba_warehouse = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                    lambda
                        r: r.is_fba_warehouse and r.partner_id.country_id.id == inv_store_wh.id)
                if not fba_warehouse:
                    fba_warehouse = self.get_fba_warehouse(view_location_id, lot_stock_id, False,
                                                           unsellable_location, inv_store_wh)
                fba_warehouse.write({'resupply_wh_ids': warehouse.ids})
            for marketplace in self.mci_efn_marketplace_ids:
                instance_exist = self.seller_id.instance_ids.filtered( \
                    lambda x: x.marketplace_id.id == marketplace.id)
                if instance_exist:
                    raise UserError(_('Instance already exist for %s with given Credential.' % ( \
                        marketplace.name)))
                wh_for_mkt = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                    lambda
                        r: r.is_fba_warehouse and r.partner_id.country_id.id == marketplace.country_id.id)
                if not wh_for_mkt:
                    wh_for_mkt = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                        lambda
                            r: r.is_fba_warehouse and r.partner_id.country_id.id == self.seller_id.country_id.id)
                vals = self.prepare_amazon_marketplace_vals(marketplace, warehouse_id)
                if marketplace.market_place_id in ['A1805IZSGTT6HS']:
                    de_fba_wh = self.seller_id.mapped('amz_warehouse_ids').filtered( \
                        lambda r: r.is_fba_warehouse and r.partner_id.country_id.code == 'DE')
                    wh_for_mkt = de_fba_wh if de_fba_wh else wh_for_mkt

                wh_for_mkt and vals.update({'fba_warehouse_id': wh_for_mkt.id})
                instance = amazon_instance_obj.create(vals)
                amazon_instances.append(instance)
            self.seller_id.write({'amazon_program': self.amazon_program,
                                  'is_european_region': self.is_european_region})
        action = self.env.ref('amazon_ept.action_amazon_configuration', False)
        result = action.read()[0] if action else {}
        ctx = result.get('context', {}) and eval(result.get('context'))
        ctx.update({'default_amz_seller_id': self.seller_id.id})
        result['context'] = ctx
        return True

    def auto_configure_stock_adjustment(self):
        """
        This Method relocate auto configure stock adjustment configuration.
        :return: This Method return Boolean(True/False).
        """
        stock_warehouse_obj = self.env['stock.warehouse']
        stock_location_obj = self.env['stock.location']
        amazon_stock_reason_group = self.env['amazon.adjustment.reason.group'].search([])
        stock_adj_email_template = self.env.ref( \
            'amazon_ept.email_template_amazon_stock_adjustment_email_ept')
        amz_seller_id = self.seller_id.id
        amz_stock_adjustment_config = self.env['amazon.stock.adjustment.config'].search(
            [('seller_id', '=', amz_seller_id), ('group_id', 'in', amazon_stock_reason_group.ids)])
        if not amz_stock_adjustment_config:
            for stock_reason_group in amazon_stock_reason_group:
                if stock_reason_group.name == 'Damaged Inventory':
                    amazon_warehouse = self.seller_id.amz_warehouse_ids.filtered( \
                        lambda l: l.partner_id.country_id.id == self.seller_id.country_id.id)
                    if not amazon_warehouse:
                        amazon_warehouse = stock_warehouse_obj.search(
                            [('seller_id', '=', amz_seller_id)], limit=1)
                    amz_warehouse_lot_stock_id = amazon_warehouse.lot_stock_id
                    self.create_adjustment_config(amz_seller_id, stock_reason_group,
                                                  amz_warehouse_lot_stock_id)

                if stock_reason_group.name == 'Unrecoverable Inventory':
                    location_type = 'inventory'
                    unrecoverable_inv_location = self.search_stock_location(location_type)
                    self.create_adjustment_config(amz_seller_id, stock_reason_group,
                                                  unrecoverable_inv_location)
                if stock_reason_group.name == 'Inbound Shipment Receive Adjustments':
                    location_type = 'transit'
                    shipment_transit_location = self.search_stock_location(location_type)
                    if not shipment_transit_location:
                        loc_vals = {
                            'name': 'FBA Transit Location %s(%s)' % ( \
                                self.seller_id.country_id.name, self.seller_id.name),
                            'usage': 'transit',
                            'company_id': self.seller_id.company_id.id,
                            'location_id': self.env.ref('stock.stock_location_locations').id
                        }
                        shipment_transit_location = stock_location_obj.create(loc_vals)
                    self.create_adjustment_config(amz_seller_id, stock_reason_group,
                                                  shipment_transit_location)
                if stock_reason_group.name == 'Software Corrections':
                    if stock_adj_email_template:
                        location_id = False
                        is_send_email = True
                        self.create_adjustment_config(amz_seller_id, stock_reason_group,
                                                      location_id, is_send_email,
                                                      stock_adj_email_template)
                if stock_reason_group.name == 'Transferring ownership':
                    location_type = 'customer'
                    customer_location = self.search_stock_location(location_type)
                    if customer_location:
                        self.create_adjustment_config(amz_seller_id, stock_reason_group,
                                                      customer_location)
                if stock_reason_group.name == 'Catalogue Management':
                    if stock_adj_email_template:
                        location_id = False
                        is_send_email = True
                        self.create_adjustment_config(amz_seller_id, stock_reason_group,
                                                      location_id, is_send_email,
                                                      stock_adj_email_template)
                if stock_reason_group.name == 'Misplaced and Found':
                    loc_vals = {
                        'name': 'FBA Lost by Amazon %s(%s)' % ( \
                            self.seller_id.country_id.name, self.seller_id.name),
                        'usage': 'internal',
                        'company_id': self.seller_id.company_id.id,
                        'location_id': self.env.ref('stock.stock_location_locations').id
                    }
                    misplaced_transit_location = stock_location_obj.create(loc_vals)
                    self.create_adjustment_config(amz_seller_id, stock_reason_group,
                                                  misplaced_transit_location)
        return True

    def search_stock_location(self, location_type):
        """
        This Method relocate search stock location based on location type.
        :param location_type: This Argument relocate location type of stock location.
        :return: This Method return search result of stock location.
        """
        stock_location_obj = self.env['stock.location']
        return stock_location_obj.search([('usage', '=', location_type)], limit=1)

    def create_adjustment_config(self, seller, stock_reason_group, location_id, is_send_email=False,
                                 email_template_id=False):
        """
        This Method relocate create stock adjustment configuration seller wise.
        :param seller: This Argument relocate amazon seller.
        :param stock_reason_group: This Argument relocate amazon stock reason group.
        :param location_id: This Argument location id.
        :param is_send_email: This Argument relocate is send email True.
        :param email_template_id: This Argument relocate email template id of stock adjustment.
        :return: This Argument return Boolean(True/False).
        """
        amz_stock_adjustment_config = self.env['amazon.stock.adjustment.config']
        amz_stock_adjustment_config.create(
            {'seller_id': seller and seller,
             'group_id': stock_reason_group and stock_reason_group.id,
             'is_send_email': is_send_email,
             'email_template_id': email_template_id and email_template_id.id,
             'location_id': location_id and location_id.id})
        return True
