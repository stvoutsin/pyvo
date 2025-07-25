# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This file contains xml element classes as defined in the VOResource standard.
"""
from functools import partial

from astropy.utils.collections import HomogeneousList
from astropy.time import Time, TimeDelta

from ...utils.xml.elements import (
    xmlattribute, xmlelement, Element, ContentMixin)

uwselement = partial(xmlelement, ns='uws')


def XSInDate(val):
    if not val:
        return None

    try:
        return Time(val, format='iso')
    except ValueError:
        pass

    try:
        return Time(val, format='isot')
    except ValueError:
        pass

    raise ValueError(f'Cannot parse datetime {val}')


InDuration = partial(TimeDelta, format='sec')
XSOutDate = partial(Time, out_subfmt='date')


__all__ = [
    'UWSElement', 'Reference', 'JobSummary', 'Parameters', 'Parameter',
    'Results', 'Result', 'ExtensibleUWSElement', 'Jobs', 'JobInfo']


def _convert_boolean(value, default=None):
    return {
        'false': False,
        '0': False,
        'true': True,
        '1': True
    }.get(value, default)


class UWSElement(Element):
    def __init__(self, config=None, pos=None, _name='', _ns='uws', **kwargs):
        super().__init__(config, pos, _name, 'uws', **kwargs)


class Reference(UWSElement):
    """standard xlink references"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type = kwargs.get('xlink:type')
        self.href = kwargs.get('xlink:href')

    @xmlattribute(name='xlink:type')
    def type(self):
        """the type of the result"""
        return self._type

    @type.setter
    def type(self, type_):
        self._type = type_

    @xmlattribute(name='xlink:href')
    def href(self):
        """the url the result can be retrieved"""
        return self._href

    @href.setter
    def href(self, href):
        self._href = href


class JobSummary(Element):
    def __init__(self, config=None, pos=None, _name='job', **kwargs):
        super().__init__(config, pos, _name, **kwargs)
        self.jobid = kwargs.get('id')
        self._runid = None
        self._ownerid = None
        self._phase = None
        self._quote = None
        self._creationtime = None
        self._starttime = None
        self._endtime = None
        self._executionduration = None
        self._destruction = None
        self._parameters = Parameters()
        self._results = Results()
        self._errorsummary = None
        self._message = None
        self._jobinfo = None

    @uwselement(name='jobId', plain=True)
    def jobid(self):
        """
        The identifier for the job
        """
        return self._jobid

    @jobid.setter
    def jobid(self, jobid):
        self._jobid = jobid

    @uwselement(name='runId', plain=True)
    def runid(self):
        """client supplied identifier"""
        return self._runid

    @runid.setter
    def runid(self, runid):
        self._runid = runid

    @uwselement(name='ownerId', plain=True)
    def ownerid(self):
        """the owner (creator) of the job"""
        return self._ownerid

    @ownerid.setter
    def ownerid(self, ownerid):
        self._ownerid = ownerid

    @uwselement(plain=True)
    def phase(self):
        """the execution phase"""
        return self._phase

    @phase.setter
    def phase(self, phase):
        self._phase = phase

    @uwselement(plain=True)
    def quote(self):
        """estimated completion time"""
        return self._quote

    @quote.setter
    def quote(self, quote):
        self._quote = XSInDate(quote)

    @quote.formatter
    def quote(self):
        try:
            return str(XSOutDate(self._quote))
        except ValueError:
            return None

    @uwselement(name='creationTime', plain=True)
    def creationtime(self):
        """The instant at which the job was created."""
        return self._creationtime

    @creationtime.setter
    def creationtime(self, creationtime):
        self._creationtime = XSInDate(creationtime)

    @creationtime.formatter
    def creationtime(self):
        try:
            return str(XSOutDate(self._creationtime))
        except ValueError:
            return None

    @uwselement(name='startTime', plain=True)
    def starttime(self):
        """The instant at which the job started execution."""
        return self._starttime

    @starttime.setter
    def starttime(self, starttime):
        self._starttime = XSInDate(starttime)

    @starttime.formatter
    def starttime(self):
        try:
            return str(XSOutDate(self._starttime))
        except ValueError:
            return None

    @uwselement(name='endTime', plain=True)
    def endtime(self):
        """The instant at which the job finished execution"""
        return self._endtime

    @endtime.setter
    def endtime(self, endtime):
        self._endtime = XSInDate(endtime)

    @endtime.formatter
    def endtime(self):
        try:
            return str(XSOutDate(self._endtime))
        except ValueError:
            return None

    @uwselement(name='executionDuration', plain=True)
    def executionduration(self):
        """
        The duration (in seconds) for which the job should be allowed to run -
        a value of 0 is intended to mean unlimited
        """
        return self._executionduration

    @executionduration.setter
    def executionduration(self, executionduration):
        if not isinstance(executionduration, TimeDelta):
            executionduration = InDuration(float(executionduration))

        self._executionduration = executionduration

    @executionduration.formatter
    def executionduration(self):
        if self.executionduration:
            return str(int(self._executionduration.value))

    @uwselement(plain=True)
    def destruction(self):
        """The time at which the whole job will be destroyed"""
        return self._destruction

    @destruction.setter
    def destruction(self, destruction):
        self._destruction = XSInDate(destruction)

    @destruction.formatter
    def destruction(self):
        try:
            return str(XSOutDate(self._destruction))
        except ValueError:
            return None

    @uwselement
    def parameters(self):
        """The parameters to the job"""
        return self._parameters

    @parameters.adder
    def parameters(self, iterator, tag, data, config, pos):
        parameters = Parameters(config, pos, 'parameters', **data)
        parameters.parse(iterator, config)
        self._parameters = parameters

    @uwselement
    def results(self):
        """The results for the job"""
        return self._results

    @results.adder
    def results(self, iterator, tag, data, config, pos):
        results = Results(config, pos, 'results', **data)
        results.parse(iterator, config)
        self._results = results

    @uwselement(name='errorSummary', plain=True)
    def errorsummary(self):
        """The error summary of the job."""
        return self._errorsummary

    @errorsummary.adder
    def errorsummary(self, iterator, tag, data, config, pos):
        res = ErrorSummary(config, pos, 'errorSummary', **data)
        res.parse(iterator, config)
        self._errorsummary = res

    @uwselement(name='jobInfo', plain=True)  # ← Add plain=True
    def jobinfo(self):
        """Implementation-specific job information"""
        return self._jobinfo

    @jobinfo.adder
    def jobinfo(self, iterator, tag, data, config, pos):
        jobinfo = JobInfo(config, pos, 'jobInfo', **data)
        jobinfo.parse(iterator, config)
        self._jobinfo = jobinfo


class Jobs(HomogeneousList, UWSElement):
    """A parsed representation of the joblist endpoint.
    """
    def __init__(self, config=None, pos=None, _name='jobs', **kwargs):
        HomogeneousList.__init__(self, JobSummary)
        UWSElement.__init__(self, config, pos, _name, **kwargs)

    @uwselement
    def jobs(self):
        return self

    @jobs.adder
    def jobs(self, iterator, tag, data, config, pos):
        return

    @uwselement(name='jobref')
    def joblist(self):
        return self

    @joblist.adder
    def joblist(self, iterator, tag, data, config, pos):
        job = JobSummary(config, pos, 'jobref', **data)
        job.parse(iterator, config)
        self.append(job)


class Parameters(UWSElement, HomogeneousList):
    """
    Parameters element of a job
    """
    def __init__(self, config=None, pos=None, _name='parameters', **kwargs):
        """ """
        # Note: Above is a load-bearing empty comment.
        # Do not remove, or else the Sphinx build may fail (see PR #193).
        HomogeneousList.__init__(self, Parameter)
        UWSElement.__init__(self, config, pos, _name, **kwargs)

    @uwselement(name='parameter')
    def parameters(self):
        return self

    @parameters.adder
    def parameters(self, iterator, tag, data, config, pos):
        parameter = Parameter(config, pos, 'parameter', **data)
        parameter.parse(iterator, config)
        self.append(parameter)


class Parameter(ContentMixin, UWSElement):
    def __init__(self, config=None, pos=None, _name='parameter', **kwargs):
        super().__init__(config, pos, _name, **kwargs)

        self.byreference = _convert_boolean(kwargs.get('byReference'))
        self.id_ = kwargs.get('id')

    @xmlattribute
    def byreference(self):
        """
        if this attribute is true then the content of the parameter represents
        a URL to retrieve the actual parameter value.
        """
        return self._byreference

    @byreference.setter
    def byreference(self, byreference):
        self._byreference = byreference

    @xmlattribute(name='id')
    def id_(self):
        """the identifier for the parameter"""
        return self._id

    @id_.setter
    def id_(self, id_):
        self._id = id_


class Results(UWSElement, HomogeneousList):
    """ """
    def __init__(self, config=None, pos=None, _name='results', **kwargs):
        HomogeneousList.__init__(self, Result)
        UWSElement.__init__(self, config, pos, _name, **kwargs)

    @uwselement(name='result')
    def results(self):
        return self

    @results.adder
    def results(self, iterator, tag, data, config, pos):
        result = Result(config, pos, 'result', **data)
        result.parse(iterator, config)
        self.append(result)


class Result(Reference, UWSElement):
    """A reference to a UWS result."""
    def __init__(self, config=None, pos=None, _name='result', **kwargs):
        super().__init__(config, pos, _name, **kwargs)

        self.id_ = kwargs.get('id')
        self.size = int(kwargs.get('size') or 0)
        self.mimetype = kwargs.get('mime-type')

    @xmlattribute(name='id')
    def id_(self):
        """the identifier for the result"""
        return self._id

    @id_.setter
    def id_(self, id_):
        self._id = id_

    @xmlattribute
    def size(self):
        """the size of the result"""
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @xmlattribute
    def mimetype(self):
        """the mimetype of the result"""
        return self._mimetype

    @mimetype.setter
    def mimetype(self, mimetype):
        self._mimetype = mimetype


class ErrorSummary(UWSElement):
    """A UWS Error summary."""
    def __init__(self, config=None, pos=None, _name='errorSummary', **kwargs):
        super().__init__(config, pos, _name, **kwargs)

        self.type_ = kwargs.get('type')
        self.has_detail = _convert_boolean(kwargs.get('hasDetail'))
        self.message = None

    @xmlattribute(name='type')
    def type_(self):
        """the type of the error"""
        return self._type

    @type_.setter
    def type_(self, type_):
        self._type = type_

    @xmlattribute
    def has_detail(self):
        """whether error has details"""
        return self._has_detail

    @has_detail.setter
    def has_detail(self, has_detail):
        self._has_detail = has_detail

    @uwselement(name='message')
    def message(self):
        """The error message"""
        return self._message

    @message.setter
    def message(self, message):
        self._message = message


class Message(ContentMixin, UWSElement):
    """The actual UWS Error message."""
    def __init__(self, config=None, pos=None, _name='message', **kwargs):
        super().__init__(config, pos, _name, **kwargs)


class ExtensibleUWSElement(ContentMixin, UWSElement):
    """
    UWS Element that can handle arbitrary child elements.
    """
    def __init__(self, config=None, pos=None, _name='', **kwargs):
        super().__init__(config, pos, _name, **kwargs)
        self._elements = {}
        self._text_content = None
        self._name = _name

    def _add_unknown_tag(self, iterator, tag, data, config, pos):
        """Handle unknown tags without generating warnings

        Parameters
        ----------
        iterator : iterator
            The iterator that provides the XML elements.
        tag : str
            The tag name of the unknown element.
        data : dict
            Additional data associated.
        config : dict
            Configuration options.
        pos : tuple
            The position of the element in the XML document (line, column).

        Returns
        -------
        ExtensibleUWSElement object
        """
        element = ExtensibleUWSElement(config, pos, tag, **data)
        element.parse(iterator, config)

        # Last element with the same tag wins
        self._elements[tag] = element
        return element

    def parse(self, iterator, config):
        """Override parse to capture text content for leaf elements"""
        super().parse(iterator, config)

        # Capture text content from ContentMixin
        if hasattr(self, 'content') and self.content is not None:
            if isinstance(self.content, str):
                self._text_content = self.content.strip()
            else:
                self._text_content = str(self.content).strip() if self.content else None

    @property
    def text(self):
        """Get the text content of this element"""
        if self._text_content is not None and self._text_content.strip():
            return self._text_content
        if hasattr(self, 'content') and self.content is not None:
            content_str = str(self.content).strip()
            return content_str if content_str else None
        return None

    @property
    def value(self):
        """Get the text content converted to appropriate type"""
        text = self.text
        if not text:
            return None

        # Try to convert to int, float, if not leave as string
        try:
            return int(text)
        except ValueError:
            try:
                return float(text)
            except ValueError:
                return text

    def get(self, name, default=None):
        """Get element by name (supports both local names and full namespaced names)"""
        return self._elements.get(name, default)

    def keys(self):
        """Return all available keys (both local and namespaced)"""
        return list(self._elements.keys())

    def __contains__(self, name):
        """Support 'in' operator"""
        return name in self._elements

    def __getitem__(self, name):
        """Dict-like access"""
        if name not in self._elements:
            raise KeyError(f"Element '{name}' not found")
        return self._elements[name]

    def __str__(self):
        if self._text_content:
            return self._text_content
        return f"<{self._name} with {len(set(self._elements.values()))} children>"

    def __repr__(self):
        unique_elements = len(set(self._elements.values()))
        return f"ExtensibleUWSElement(name='{self._name}', elements={unique_elements})"


class JobInfo(ExtensibleUWSElement):
    """JobInfo element that can contain arbitrary elements."""
    def __init__(self, config=None, pos=None, _name='jobInfo', **kwargs):
        super().__init__(config, pos, _name, **kwargs)
