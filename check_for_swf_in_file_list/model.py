import attr
import typing

# see https://www.attrs.org/en/stable/glossary.html#term-slotted-classes
@attr.s(auto_attribs=True, frozen=True, kw_only=True, slots=True)
class UrlListEntry:
    full_url:str = attr.ib()
    was_fixed:bool = attr.ib()


@attr.s(auto_attribs=True, frozen=True, kw_only=True, slots=True)
class IndividualTestResult:
    url_tested:UrlListEntry = attr.ib()
    first_three_bytes:bytes = attr.ib()
    is_swf:bool = attr.ib()
    requests_error:bool = attr.ib()
    error_str:typing.Optional[str] = attr.ib()

@attr.s(auto_attribs=True, frozen=True, kw_only=True, slots=True)
class DomainTestResults:

    domain:str = attr.ib()
    test_results:typing.Sequence[IndividualTestResult] = attr.ib()
    num_matches:int = attr.ib()
    num_failures:int = attr.ib()
    total:int = attr.ib()

@attr.s(auto_attribs=True, frozen=True, kw_only=True, slots=True)
class AllResults:
    results:typing.Sequence[DomainTestResults] = attr.ib()
