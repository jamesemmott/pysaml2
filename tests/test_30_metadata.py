import os

from saml2 import metadata, utils
from saml2 import NAMESPACE as SAML2_NAMESPACE
from saml2 import BINDING_SOAP
from saml2 import md, saml, samlp
from saml2 import time_util
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from py.test import raises

SWAMI_METADATA = "swamid-kalmar-1.0.xml"
INCOMMON_METADATA = "InCommon-metadata.xml"
EXAMPLE_METADATA = "metadata_example.xml"
SWITCH_METADATA = "metadata.aaitest.xml"
SP_METADATA = "metasp.xml"

def _eq(l1,l2):
    return set(l1) == set(l2)
    
def _read_file(name):
    try:
        return open(name).read()
    except IOError:
        name = "tests/"+name
        return open(name).read()

def _read_lines(name):
    try:
        return open(name).readlines()
    except IOError:
        name = "tests/"+name
        return open(name).readlines()
        
def test_swami_1():
    md = metadata.MetaData()
    md.import_metadata(_read_file(SWAMI_METADATA))
    print len(md.entity)
    assert len(md.entity)
    idps = dict([(id,ent["idp_sso"]) for id,ent in md.entity.items() \
                if "idp_sso" in ent])
    print idps
    assert idps.keys()
    idp_sso = md.single_sign_on_services(
                    'https://idp.umu.se/saml2/idp/metadata.php')
    assert md.name('https://idp.umu.se/saml2/idp/metadata.php') == (
        u'Ume\xe5 university (New SAML2)')
    assert len(idp_sso) == 1
    assert idp_sso == ['https://idp.umu.se/saml2/idp/SSOService.php']
    ssocerts =  md.certs('https://idp.umu.se/saml2/idp/SSOService.php')
    print ssocerts
    assert len(ssocerts) == 1
    
def test_incommon_1():
    md = metadata.MetaData()
    md.import_metadata(_read_file(INCOMMON_METADATA))
    print len(md.entity)
    assert len(md.entity) == 442
    idps = dict([
        (id,ent["idp_sso"]) for id,ent in md.entity.items() if "idp_sso" in ent])
    print idps.keys()
    assert len(idps) == 53 # !!!!???? < 10%
    raises(KeyError, "md.single_sign_on_services('urn:mace:incommon:uiuc.edu')")
    idp_sso = md.single_sign_on_services('urn:mace:incommon:alaska.edu')
    assert len(idp_sso) == 1
    print idp_sso
    assert idp_sso == ['https://idp.alaska.edu/idp/profile/SAML2/Redirect/SSO']

def test_example():
    md = metadata.MetaData()
    md.import_metadata(_read_file(EXAMPLE_METADATA))
    print len(md.entity)
    assert len(md.entity) == 1
    idps = dict([(id,ent["idp_sso"]) for id,ent in md.entity.items() \
                if "idp_sso" in ent])
    assert idps.keys() == [
            'http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php']
    certs = md.certs(
            'http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php')
    assert len(certs) == 1
    assert isinstance(certs[0], tuple)
    assert len(certs[0]) == 2
        
def test_switch_1():
    md = metadata.MetaData()
    md.import_metadata(_read_file(SWITCH_METADATA))
    print len(md.entity)
    assert len(md.entity) == 90
    idps = dict([(id,ent["idp_sso"]) for id,ent in md.entity.items() \
                if "idp_sso" in ent])
    print idps.keys()
    idp_sso = md.single_sign_on_services(
        'https://aai-demo-idp.switch.ch/idp/shibboleth')
    assert len(idp_sso) == 1
    print idp_sso
    assert idp_sso == [
        'https://aai-demo-idp.switch.ch/idp/profile/SAML2/Redirect/SSO']
    assert len(idps) == 16
    aas = dict([(id,ent["attribute_authority"]) for id,ent in md.entity.items() \
                if "attribute_authority" in ent])
    print aas.keys()
    aads = aas['https://aai-demo-idp.switch.ch/idp/shibboleth']
    assert len(aads) == 1
    aad = aads[0]
    assert len(aad.attribute_service) == 1
    assert len(aad.name_id_format) == 2
    dual = dict([(id,ent) for id,ent in md.entity.items() \
                if "idp_sso" in ent and "sp_sso" in ent])
    print len(dual)
    assert len(dual) == 0

def test_sp_metadata():
    md = metadata.MetaData()
    md.import_metadata(_read_file(SP_METADATA))
    
    print md.entity
    assert len(md.entity) == 1
    assert md.entity.keys() == ['urn:mace:umu.se:saml:roland:sp']
    assert md.entity['urn:mace:umu.se:saml:roland:sp'].keys() == [
                                                    "organization","sp_sso"]
    print md.entity['urn:mace:umu.se:saml:roland:sp']["sp_sso"][0].keyswv()
    (req,opt) = md.attribute_consumer('urn:mace:umu.se:saml:roland:sp')
    print req
    assert len(req) == 3
    assert len(opt) == 1
    assert opt[0].name == 'urn:oid:2.5.4.12'
    assert opt[0].friendly_name == 'title'
    assert _eq([n.name for n in req],['urn:oid:2.5.4.4', 'urn:oid:2.5.4.42', 
                                        'urn:oid:0.9.2342.19200300.100.1.3'])
    assert _eq([n.friendly_name for n in req],['surName', 'givenName', 'mail'])

# ------------ Constructing metaval ----------------------------------------

def test_construct_organisation_name():
    o = md.Organization()
    utils.make_vals({"text":"Exempel AB", "lang":"se"},
                        md.OrganizationName, o, "organization_name")
    print o
    assert str(o) == """<?xml version='1.0' encoding='UTF-8'?>
<ns0:Organization xmlns:ns0="urn:oasis:names:tc:SAML:2.0:metadata"><ns0:OrganizationName ns1:lang="se" xmlns:ns1="http:#www.w3.org/XML/1998/namespace">Exempel AB</ns0:OrganizationName></ns0:Organization>"""

def test_make_int_value():
    val = utils.make_vals( 1, saml.AttributeValue, part=True) 
    assert isinstance(val, saml.AttributeValue)
    assert val.text == "1"

def test_make_true_value():
    val = utils.make_vals( True, saml.AttributeValue, part=True ) 
    assert isinstance(val, saml.AttributeValue)
    assert val.text == "True"

def test_make_false_value():
    val = utils.make_vals( False, saml.AttributeValue, part=True ) 
    assert isinstance(val, saml.AttributeValue)
    assert val.text == "False"

NO_VALUE = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:AttributeValue xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion" />"""

def test_make_no_value():
    val = utils.make_vals( None, saml.AttributeValue, part=True ) 
    assert isinstance(val, saml.AttributeValue)
    assert val.text == None
    print val
    assert "%s" % val == NO_VALUE

def test_make_string():
    val = utils.make_vals( "example", saml.AttributeValue, part=True ) 
    assert isinstance(val, saml.AttributeValue)
    assert val.text == "example"

def test_make_list_of_strings():
    attr = saml.Attribute()
    vals = ["foo", "bar"]
    val = utils.make_vals(vals, saml.AttributeValue, attr, 
                                "attribute_value") 
    assert attr.keyswv() == ["attribute_value"]
    print attr.attribute_value
    assert _eq([val.text for val in attr.attribute_value], vals)

def test_make_dict():
    vals = ["foo", "bar"]
    attrval = { "attribute_value": vals}
    attr = utils.make_vals(attrval, saml.Attribute, part=True) 
    assert attr.keyswv() == ["attribute_value"]
    assert _eq([val.text for val in attr.attribute_value], vals)

# ------------ Constructing metadata ----------------------------------------

def test_construct_contact():
    c = utils.make_instance(md.ContactPerson, {
        "given_name":"Roland",
        "sur_name": "Hedberg",
        "email_address": "roland@catalogix.se",
    })
    print c
    assert c.given_name.text == "Roland"
    assert c.sur_name.text == "Hedberg"
    assert c.email_address[0].text == "roland@catalogix.se"    
    assert _eq(c.keyswv(), ["given_name","sur_name","email_address"])

            
def test_construct_organisation():
    c = utils.make_instance( md.Organization, {
            "organization_name": ["Example Co.",
                    {"text":"Exempel AB", "lang":"se"}],
            "organization_url": "http://www.example.com/"
        })
        
    assert _eq(c.keyswv(), ["organization_name","organization_url"])
    assert len(c.organization_name) == 2
    org_names = [on.text for on in c.organization_name]
    assert _eq(org_names,["Exempel AB","Example Co."])
    assert len(c.organization_url) == 1
    
def test_construct_entity_descr_1():
    ed = utils.make_instance(md.EntityDescriptor,
        {"organization": {
            "organization_name":"Catalogix", 
            "organization_url": "http://www.catalogix.se/"},
         "entity_id": "urn:mace:catalogix.se:sp1",   
        })

    assert ed.entity_id == "urn:mace:catalogix.se:sp1"
    org = ed.organization
    assert _eq(org.keyswv(), ["organization_name","organization_url"])
    assert len(org.organization_name) == 1
    assert org.organization_name[0].text == "Catalogix"
    assert org.organization_url[0].text == "http://www.catalogix.se/"

def test_construct_entity_descr_2():
    ed = utils.make_instance(md.EntityDescriptor,
        {"organization": {
            "organization_name":"Catalogix", 
            "organization_url": "http://www.catalogix.se/"},
         "entity_id": "urn:mace:catalogix.se:sp1",
         "contact_person": {
            "given_name":"Roland",
            "sur_name": "Hedberg",
            "email_address": "roland@catalogix.se",
            }   
        })

    assert _eq(ed.keyswv(), ["entity_id", "contact_person", "organization"])
    assert ed.entity_id == "urn:mace:catalogix.se:sp1"
    org = ed.organization
    assert _eq(org.keyswv(), ["organization_name", "organization_url"])
    assert len(org.organization_name) == 1
    assert org.organization_name[0].text == "Catalogix"
    assert org.organization_url[0].text == "http://www.catalogix.se/"
    assert len(ed.contact_person) == 1
    c = ed.contact_person[0]
    assert c.given_name.text == "Roland"
    assert c.sur_name.text == "Hedberg"
    assert c.email_address[0].text == "roland@catalogix.se"    
    assert _eq(c.keyswv(), ["given_name","sur_name","email_address"])

def test_construct_key_descriptor():
    cert = "".join(_read_lines("test.pem")[1:-1]).strip()
    spec = {
        "use": "signing",
        "key_info" : {
            "x509_data": {
                "x509_certificate": cert
            }
        }
    }
    kd = utils.make_instance(md.KeyDescriptor, spec)
    assert _eq(kd.keyswv(), ["use", "key_info"])
    assert kd.use == "signing"
    ki = kd.key_info
    assert _eq(ki.keyswv(), ["x509_data"])
    assert len(ki.x509_data) == 1
    data = ki.x509_data[0]
    assert _eq(data.keyswv(), ["x509_certificate"])
    assert len(data.x509_certificate) == 1
    assert len(data.x509_certificate[0].text.strip()) == len(cert)

def test_construct_key_descriptor_with_key_name():
    cert = "".join(_read_lines("test.pem")[1:-1]).strip()
    spec = {
        "use": "signing",
        "key_info" : {
            "key_name": "example.com",
            "x509_data": {
                "x509_certificate": cert
            }
        }
    }
    kd = utils.make_instance(md.KeyDescriptor, spec)
    assert _eq(kd.keyswv(), ["use", "key_info"])
    assert kd.use == "signing"
    ki = kd.key_info
    assert _eq(ki.keyswv(), ["x509_data", "key_name"])
    assert len(ki.key_name) == 1
    assert ki.key_name[0].text.strip() == "example.com"
    assert len(ki.x509_data) == 1
    data = ki.x509_data[0]
    assert _eq(data.keyswv(), ["x509_certificate"])
    assert len(data.x509_certificate) == 1
    assert len(data.x509_certificate[0].text.strip()) == len(cert)
    
def test_construct_AttributeAuthorityDescriptor():
    aad = utils.make_instance(
            md.AttributeAuthorityDescriptor, {
                "valid_until": time_util.in_a_while(30), # 30 days from now
                "id": "aad.example.com",
                "protocol_support_enumeration": SAML2_NAMESPACE,
                "attribute_service": {
                    "binding": BINDING_SOAP,
                    "location": "http://example.com:6543/saml2/aad",
                },
                "name_id_format":[
                    NAMEID_FORMAT_TRANSIENT,
                ],
                "key_descriptor": {
                    "use": "signing",
                    "key_info" : {
                        "key_name": "example.com",
                    }
                }
            })

    print aad
    assert _eq(aad.keyswv(),["valid_until", "id", "attribute_service",
                            "name_id_format", "key_descriptor",
                            "protocol_support_enumeration"])
    assert time_util.str_to_time(aad.valid_until)
    assert aad.id == "aad.example.com"
    assert aad.protocol_support_enumeration == SAML2_NAMESPACE
    assert len(aad.attribute_service) == 1
    atsr = aad.attribute_service[0]
    assert _eq(atsr.keyswv(),["binding", "location"])
    assert atsr.binding == BINDING_SOAP
    assert atsr.location == "http://example.com:6543/saml2/aad"
    assert len(aad.name_id_format) == 1
    nif = aad.name_id_format[0]
    assert nif.text.strip() == NAMEID_FORMAT_TRANSIENT
    assert len(aad.key_descriptor) == 1
    kdesc = aad.key_descriptor[0]
    assert kdesc.use == "signing"
    assert kdesc.key_info.key_name[0].text.strip() == "example.com"
    
STATUS_RESULT = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:Status xmlns:ns0="urn:oasis:names:tc:SAML:2.0:protocol"><ns0:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Responder"><ns0:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:UnknownPrincipal" /></ns0:StatusCode><ns0:StatusMessage>Error resolving principal</ns0:StatusMessage></ns0:Status>"""

def test_status():
    input = {
        "status_code": {
            "value": samlp.STATUS_RESPONDER,
            "status_code":
                {
                "value": samlp.STATUS_UNKNOWN_PRINCIPAL,
                },
        },
        "status_message": "Error resolving principal",
        }
    status_text = "%s" % utils.make_instance( samlp.Status, input)
    assert status_text == STATUS_RESULT
    