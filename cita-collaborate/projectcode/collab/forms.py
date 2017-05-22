from django import forms
import datetime
import re

from django.forms.widgets import Widget, Select
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

MONTHS = {
    '':_(' '), 
    1:_('January'), 2:_('February'), 3:_('March'), 4:_('April'), 5:_('May'), 6:_('June'),
    7:_('July'), 8:_('August'), 9:_('September'), 10:_('October'), 11:_('November'),
    12:_('December')
}


class DeleteForm(forms.Form):
    """Generic form for deleting objects
    I don't actually need the "sure" field, but I'll leave it 
    here to avoid worrying about breaking anything."""
    
    sure = forms.CharField(max_length=10,  widget=forms.HiddenInput)
    
class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    """This field is used wherever one is showing a user in a multiple choice
    field. It'll show the user's profile's string representation, if he/she has filled
    out the profile."""
    
    def label_from_instance(self, obj):
        try:
            return "%s " % obj.profile.all()[0]#obj.username
        except IndexError:
            return "%s " % obj.username

class UserChoiceField(forms.ModelChoiceField):
    """This field is used wherever one is showing a user in a multiple choice
    field. It'll show the user's profile's string representation, if he/she has filled
    out the profile."""
    
    def label_from_instance(self, obj):
        try:
            return "%s " % obj.profile.all()[0]#obj.username
        except IndexError:
            return "%s " % obj.username

class SelectDateWidget(Widget):
    """
    A Widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    
    This is taken straight from the Django source code and modified. The 
    problem with the Django one is that it doesn't allow for a blank input.
    """
    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year+10)
        

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            year_val = month_val = day_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = MONTHS.items()
        month_choices.sort()
        month_choices.insert(0, month_choices[-1])
        del(month_choices[-1])
        local_attrs = self.build_attrs(id=self.month_field % id_)
        select_html = Select(choices=month_choices).render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        day_choices = [(i, i) for i in range(1, 32)]
        day_choices.insert(0, ('', ''))
        local_attrs['id'] = self.day_field % id_
        select_html = Select(choices=day_choices).render(self.day_field % name, day_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        year_choices.insert(0, ('', ''))
        local_attrs['id'] = self.year_field % id_
        select_html = Select(choices=year_choices).render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y, m, d = data.get(self.year_field % name), data.get(self.month_field % name), data.get(self.day_field % name)
        if y and m and d:
            return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)

class ModelFormTextArea(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """Check to see which fields have Textarea as a widget
        and set the col attribute to 72"""
        super(ModelFormTextArea, self).__init__(*args, **kwargs)
        for field in self.fields:
            if self.fields[field].widget.__class__ == forms.widgets.Textarea:
                self.fields[field].widget.attrs['cols']=72
        
