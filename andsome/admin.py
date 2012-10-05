import operator
from datetime import timedelta

from django.db.models import Q, Count
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms import Field, IntegerField
from django.http import HttpResponseRedirect
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.timezone import now
from django_extensions.admin import ForeignKeyAutocompleteAdmin

from tangy_auth.admin import TangyUser
from tangy_product.models import SubscriptionOffer, Product
from tangy_subscription.models import Subscription, SentSubscription, Address, EDMSubscription, EDMSend, Transaction, EmailTemplate, Issue, Note

class ProductFilter(admin.SimpleListFilter):
    title = 'Product'

    parameter_name = 'product'

    def lookups(self, request, model_admin):
        #filter products by sub offers (and thus are a candidate for subscriptions)
        products = Product.objects.annotate(num_sub_offers=Count('subscription_offers')).filter(num_sub_offers__gt=0)
        return [('%d' % product.pk, '%s' % product) for product in products]

    def queryset(self, request, queryset):
        try:
            product = Product.objects.get(pk = self.value())
        except Product.DoesNotExist:
            return queryset

        return Subscription.objects.filter(
            subscription_offer__in=list(
                list(SubscriptionOffer.objects.filter(product=product))
            )
        )

class IssueProductFilter(admin.SimpleListFilter):
    title = 'Product'
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        products = Product.objects.annotate(num_issues=Count('issues')).filter(num_issues__gt=0)
        return [('%d' % product.pk, '%s' % product) for product in products]

    def queryset(self, request, queryset):
        try:
            product = Product.objects.get(pk = self.value())
        except Product.DoesNotExist:
            return queryset

        return queryset.filter(product = product)

class IssueSetFilter(admin.SimpleListFilter):
    title = 'Issue'
    parameter_name = 'issue_set'

    def lookups(self, request, model_admin):
        return (('current', 'Current Issue'), ('past', 'Past Issues'), ('future', 'Future Issues'))

    #@staticmethod
    def get_issue_filter(self, current_issue_number):
        kwargs = {}
        if self.value() == 'past':
            kwargs = {'number__lt': current_issue_number}
        elif self.value() == 'future':
            kwargs = {'number__gt': current_issue_number}
        elif self.value() == 'current':
           kwargs = {'number': current_issue_number}
        return kwargs

    def queryset(self, request, queryset):
        filtered_results = queryset

        if self.value():
            if request.GET.has_key('product'):
                #already filtered by product, just filter / slice on current issue
                try:
                    product = Product.objects.get(pk=int(request.GET.get('product')))
                    current_issue = product.current_issue()
                    if current_issue:
                        filtered_results = queryset.filter(**self.get_issue_filter(current_issue.number))
                except Product.DoesNotExist:
                    pass
            else:
                #IssueProductFilter is unset, calculate current issue for each and filter via a big OR query
                # eg ... WHERE (product_id=1, number=41) OR (product_id=7, number=12) OR ...
                q_objects = []
                for product in Product.objects.annotate(num_issues=Count('issues')).filter(num_issues__gt=0):
                    current_issue = product.current_issue()

                    if current_issue:
                        q_objects.append(Q(product__pk=product.id, **self.get_issue_filter(current_issue.number)))

                reduced_q = reduce(operator.or_, q_objects)
                filtered_results = queryset.filter(reduced_q)

        return filtered_results

class SubscriptionDueFilter(admin.SimpleListFilter):
    title = 'Expiry Issue'
    parameter_name = 'issue_offset'

    def calculate_expiry_issue_number(self, product):
        expiry_issue_number = None

        current_issue = product.current_issue()
        if current_issue:
            expiry_issue_number = int(self.value()) + current_issue.number

        return expiry_issue_number

    def lookups(self, request, model_admin):
        return ((0, 'Current Issue'), (1, 'Next Issue'), (2, 'Two Issues'))

    def queryset(self, request, queryset):
        filtered_results = queryset

        if self.value():
            if request.GET.has_key('product'):
                #already filtered by product, just filter by expiry issue
                product = Product.objects.get(pk=int(request.GET.get('product')))
                expiry_issue_number = self.calculate_expiry_issue_number(product)

                if expiry_issue_number:
                    filtered_results = queryset.filter(expiry_issue__number=expiry_issue_number)
            else:
                #ProductFilter is unset, calculate expiry issue for each and filter via a big OR query
                # eg ... WHERE (exp_issue_product_id=1, exp_issue_num=41) OR (exp_issue_product_id=2, exp_issue_num=89) OR ...
                q_objects = []
                for product in Product.objects.all():
                    expiry_issue_number = self.calculate_expiry_issue_number(product)

                    if expiry_issue_number:
                        q_objects.append(Q(expiry_issue__product__pk=product.id, expiry_issue__number=expiry_issue_number))
                reduced_q = reduce(operator.or_, q_objects)
                filtered_results = queryset.filter(reduced_q)

        return filtered_results

class GiftFilter(admin.SimpleListFilter):
    title = 'Gifts Only'
    parameter_name = 'is_gift'

    def lookups(self, request, model_admin):
        return (('true', 'Is a gift'),)

    def queryset(self, request, queryset):

        if request.GET.get('is_gift') == 'true':
            return queryset.filter(gift_giver__isnull = False)

        return queryset

class TransactionStatusFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (('success', 'Succeeded'), ('failure', 'Failed'))

    def queryset(self, request, queryset):
        if request.GET.has_key('status'):
            success = request.GET.get('status') == 'success'

            return queryset.filter(success = success)

        return queryset

class DuplicateAddressFilter(admin.SimpleListFilter):
    title = 'Addresses with Duplicates'

    parameter_name = 'show_duplicates'

    def lookups(self, request, model_admin):
        return [('only_dupes', 'Only w/Duplicates')]

    def queryset(self, request, queryset):
        if request.GET.get('show_duplicates') == 'only_dupes':
            return queryset.filter(duplicate__isnull = False)

        return queryset

class AddressAdmin(ForeignKeyAutocompleteAdmin):
    exclude = ('non_duplicates', 'duplicate')
    list_display = ('address_1', 'address_2', 'city', 'country')
    list_filter = (DuplicateAddressFilter,)
    actions = ['resolve_duplicate']
    related_search_fields = {
        'user': ('email', 'first_name', 'last_name'),
    }
    search_fields = ['address_1', 'address_2', 'country']
    readonly_fields = ('e164_home_phone', 'e164_work_phone', 'e164_mobile',)

    def resolve_duplicate(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        return HttpResponseRedirect("/admin/tangy_subscription/address/resolve_duplicate?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))

    resolve_duplicate.short_description = 'Resolve duplicate for selected Users'

class SubscriptionAddressWidget(ForeignKeyRawIdWidget):
    widget_template = None

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}

        output = [super(SubscriptionAddressWidget, self).render(name, value, attrs)]


class TransactionAdminInline(admin.StackedInline):
    model = Transaction
    fk_name = 'subscription'
    extra = 1

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('transaction_date', 'amount_settlement', 'type')

        return []

from django.forms.widgets import Widget

class ProductRelatedWidget(Widget):
    def __init__(self, related_type, show_product_select = True, *args, **kwargs):
        self.related_type = related_type
        self.show_product_select = show_product_select

        super(ProductRelatedWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        s = ''

        if self.show_product_select:

            products = Product.objects.all()

            if value == None:
                current_related = []
            elif self.related_type == 'issues':
                current_related = Issue.objects.get(pk=value)
            elif self.related_type == 'subscription_offers':
                current_related = SubscriptionOffer.objects.get(pk=value)

            s += '<select class="product-select" id="product_id_%s">' % name

            for product in products:
                selected = ''

                if value != None and product == current_related.product:
                    selected = ' selected="selected"'

                s += '<option value="%s"%s>%s</option>' % (product.pk, selected, product)

            s += '</select>&nbsp;'

            product_field_sel = '#product_id_%s' % name
        else:
            product_field_sel = '.product-select'

        s += '<select name="%s" disabled="disabled" id="id_%s">' % (name, name)

        s += '<option>Loading&hellip;</option>'

        s += '</select>'

        s += """<script type="text/javascript">


                $(document).ready(function(){
                    var g_name = '%s';
                    var g_relatedType = '%s';
                    var g_selected = '%d';

                    var reloadRelated = function(){
                        $('#id_' + g_name).empty();

                        $('#id_' + g_name).html("<option>Loading&hellip;</option>");

                        $('#id_' + g_name).attr("disabled", true);

                        $.get("/admin/tangy_subscription/product/" + $('%s').val() + "/"+ g_relatedType +"/?selected=" + g_selected, function(data){
                            $('#id_' + g_name).empty();
                            var relatedData = eval(data);
                            var relatedChoices = '';

                            if(relatedData.length > 0){
                                $('#id_' + g_name).attr("disabled", false);
                                for(var i=0; i < relatedData.length; ++i){
                                    var related = relatedData[i];
                                    var selected = ((g_selected == related.pk) || ((g_selected == -1) && related.__unicode__.indexOf('(current)') != -1)) ? ' selected="selected"' : '';

                                    relatedChoices += '<option value="' + related.pk + '"' + selected + '>'  + related.__unicode__ + '</option>';
                                }
                            } else {
                                $('#id_' + g_name).attr("disabled", true);
                                relatedChoices = '<option value="-1">Select one or more products.</option>';
                            }

                            $('#id_' + g_name).html(relatedChoices);

                        }, 'json');
                    };

                    $('.product-select').change(function(){
                        reloadRelated();
                    });

                    reloadRelated();
                });
                </script>
        """ % ( name, self.related_type, value or -1, product_field_sel)

        return s

    @property
    def choices(self):
        return None

    @choices.setter
    def choices(self, value):
        pass

class ProductRelatedField(Field):
    def __init__(self, related_type, show_product_select = True, *args, **kwargs):
        self.related_type = related_type

        kwargs['widget'] = ProductRelatedWidget(related_type, show_product_select)

        super(ProductRelatedField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if self.related_type == 'issues':
            return Issue.objects.get(pk=value)
        elif self.related_type == 'subscription_offers':
            return SubscriptionOffer.objects.get(pk=value)

        return value


class UserAddressWidget(Widget):
    def __init__(self, *args, **kwargs):
        super(UserAddressWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        s = """
        <select id="id_address" disabled="disabled">
            <option value="-1">Choose a subscriber first</option>
        </select>
        <script type="text/javascript">
            $(document).ready(function(){
                var reloadAddresses = function(){


                    $.get("/admin/tangy_subscription/user_address/" + $('#id_subscriber').val(), function(data){
                        $('#id_%s').empty();

                        var relatedData = eval(data);
                        var relatedChoices = '';

                        if(relatedData.length == 0){
                            $('#id_%s').attr("disabled", true);
                            relatedChoices = '<option value="">Subscriber has no addresses.</option>';
                        } else {
                            $('#id_%s').attr("disabled", false);
                            for(var i=0; i < relatedData.length; ++i){
                                var related = relatedData[i];

                                var selected = (%d == related.pk) ? ' selected="selected"' : '';

                                relatedChoices += '<option value="' + related.pk + '"' + selected + '>'  + related.__unicode__ + '</option>';
                            }
                        }
                        $('#id_%s').html(relatedChoices);
                    }, 'json');
                };

                $('#id_subscriber, #lookup_subscriber').change(reloadAddresses);

                reloadAddresses();
            });
        </script>
        """ % (name, name, name, value or -1, name)

        return s

    @property
    def choices(self):
        return None

    @choices.setter
    def choices(self, value):
        pass

class UserAddressField(Field):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = UserAddressWidget()

        super(UserAddressField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        try:
            return Address.objects.get(pk=value)
        except:
            return value

class SubscriptionAdmin(ForeignKeyAutocompleteAdmin):
    list_filter = (ProductFilter, SubscriptionDueFilter, GiftFilter)
    search_fields = ['subscriber__name', 'gift_giver__name', 'subscriber__email', 'gift_giver__email', 'imported_id']

    raw_id_fields = ('renewal_of',)
    list_display = ('__unicode__', 'subscriber_link', 'gift_giver_link', 'subscription_offer_link')
    exclude = ('calculated_sub_price',)
    readonly_fields = ('post_import_validation_msg', 'imported_id',)

    #inlines = ( TransactionAdminInline,)

    related_search_fields = {
        'subscriber': ('email', 'name'),
        'gift_giver': ('email', 'name')
    }

    def subscriber_link(self, obj):
        return self.link_for_foreignkey(obj.subscriber)
    subscriber_link.allow_tags = True
    subscriber_link.short_description = "Gift Giver"

    def gift_giver_link(self, obj):
        return self.link_for_foreignkey(obj.gift_giver)
    gift_giver_link.allow_tags = True
    gift_giver_link.short_description = "Gift Giver"

    def subscription_offer_link(self, obj):
        return self.link_for_foreignkey(obj.subscription_offer)
    subscription_offer_link.allow_tags = True
    subscription_offer_link.short_description = "Subscription Offer"

    @staticmethod
    def link_for_foreignkey(target):
        return '' if not target else u'<a href="../../%s/%s/%d/">%s</a>' % \
            (target._meta.app_label, target._meta.module_name, target.id, unicode(target))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('first_issue', 'expiry_issue'):
            return ProductRelatedField('issues', False)
        elif db_field.name == 'subscription_offer':
            return ProductRelatedField('subscription_offers')
        elif db_field.name == 'address':
            return UserAddressField()

        return super(SubscriptionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class MultiSubOfferWidget(Widget):
    def __init__(self, *args, **kwargs):
        super(MultiSubOfferWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        products = Product.objects.all().order_by('name')

        value = value or []

        selected_sub_offers = SubscriptionOffer.objects.filter(pk__in = value)

        selected_products = []

        for sub_offer in selected_sub_offers:
            if sub_offer.product.pk not in selected_products:
                selected_products.append(sub_offer.product.pk)

        s = ''

        s += '<select multiple="multiple" id="id_%s_products">' % name

        for product in products:
            selected = ''

            if product.pk in selected_products:
                selected = ' selected="selected"'

            s += '<option value="%d"%s>%s</option>' % (product.pk, selected, product.name)

        s += '</select>&nbsp;'

        s+= '<select multiple="multiple" id="id_%s" name="%s" disabled="disabled">' % (name, name)

        s+= '<option val="-1">Select one or more products</option>'

        s+= '</select>'

        s += """
        <script type="text/javascript">
            var $ = django.jQuery;

            var g_elName = '%s';
            var g_selectedSOs = '%s';

            $(document).ready(function(){
                var reloadSubsForProducts = function(element){

                    var selectedIDs = element.val();

                    if(g_selectedSOs == '')
                        g_selectedSOs = $("#id_" + g_elName).val();

                    $("#id_" + g_elName).empty();
                    $("#id_" + g_elName).attr("disabled", true);


                    if(selectedIDs == '') {
                        $("#id_" + g_elName).html('<option value="-1">Select one or more products</option>');
                        return;
                    }

                    $("#id_" + g_elName).html('<option value="-1">Loading&hellip;</option>');
                    $("#id_" + g_elName).attr("disabled", true);

                    $.get('/admin/tangy_subscription/multi_sub_offer/?product_ids=' + selectedIDs + '&selected_sos=' + g_selectedSOs, function(data) {

                        var selectHTML = '';
                        if(data.length) {
                            for(var i = 0; i < data.length; ++i){
                                var selected = data[i].selected ? ' selected="selected"' : '';
                                selectHTML += '<option value="' + data[i].pk + '"' + selected + '>' + data[i].__unicode__ + '</option>';
                            }

                            $("#id_" + g_elName).attr("disabled", false);
                        } else {
                            selectHTML += '<option value="-1">No subscription offers for issue(s)</option>';
                            $("#id_" + g_elName).attr("disabled", true);
                        }

                        $("#id_" + g_elName).html(selectHTML);
                        g_selectedSOs = '';

                    }, 'json');
                }

                $("#id_" + g_elName + "_products").change(function(){
                    reloadSubsForProducts($(this));
                });

                reloadSubsForProducts($("#id_" + g_elName + "_products"));
            });
        </script>
        """ % (name, ','.join(map(lambda x: str(x), value)))

        return s

    @property
    def choices(self):
        try:
            return self._choices
        except:
            return []

    @choices.setter
    def choices(self, val):
        self._choices = val

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)

class MultiSubOfferField(Field):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = MultiSubOfferWidget()
        super(MultiSubOfferField, self).__init__(*args, **kwargs)

class TransactionAdmin(admin.ModelAdmin):
    list_filter = (TransactionStatusFilter,)
    raw_id_fields = ("subscription",)

    """def add_view(self, request, form_url='', extra_context=None):
        self.sub_id = request.GET.get('sub_id')

        return super(TransactionAdmin, self).add_view(request, form_url='', extra_context=None)"""

    """def get_readonly_fields(self, request, obj=None):
        if request.GET.get('sub_id'):
            return ('subscription',)

        return []"""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        form_field = super(TransactionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'subscription' and (request.GET.get('sub_id') != None):
            form_field.initial = Subscription.objects.get(pk=request.GET.get('sub_id'))

        return form_field

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(reverse('admin:tangy_subscription_subscription_change', args=(obj.subscription.id,)))

class NoteAdmin(admin.ModelAdmin):
    raw_id_fields = ("subscription", 'user')
    exclude = ('creator',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        form_field = super(NoteAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'subscription' and (request.GET.get('sub_id') != None):
            form_field.initial = Subscription.objects.get(pk=request.GET.get('sub_id'))

        if db_field.name == 'user':
            if request.GET.get('user_id') != None:
                form_field.initial = TangyUser.objects.get(pk=request.GET.get('user_id'))
            elif request.GET.get('sub_id') != None:
                form_field.initial = Subscription.objects.get(pk=request.GET.get('sub_id')).subscriber

        return form_field

    def save_model(self, request, obj, form, change):
        if change == False:
            obj.creator_id = request.user.pk
            obj.save()
        return super(NoteAdmin, self).save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        if obj.subscription:
            return HttpResponseRedirect(reverse('admin:tangy_subscription_subscription_change', args=(obj.subscription.id,)))
        else:
            return HttpResponseRedirect(reverse('admin:tangy_auth_tangyuser_change', args=(obj.user.id,)))

class IssueAdmin(admin.ModelAdmin):
    list_display = ('product', 'number', 'name', 'pub_date')
    list_filter = (IssueProductFilter, IssueSetFilter)
    fields = ('product', 'number', 'issue_of_year', 'name', 'pub_date', 'subs_plus_alias', 'imported_aliases',)
    readonly_fields = ('subs_plus_alias', 'imported_aliases',)

class SentSubscriptionAdmin(admin.ModelAdmin):
    search_fields = ['subscription__subscriber__name', 'subscription__subscriber__email']
    readonly_fields = ('subscription',)
    list_display = ('__unicode__',)


admin.site.register(EmailTemplate)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(SentSubscription, SentSubscriptionAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(EDMSubscription)
admin.site.register(EDMSend)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Note, NoteAdmin)
