// **********************************************************************
//
// Copyright (c) 2002
// MutableRealms, Inc.
// Huntsville, AL, USA
//
// All Rights Reserved
//
// **********************************************************************

#include <Ice/SecurityException.h>
#include <Ice/SslConnectionOpenSSL.h>
#include <Ice/SslContextOpenSSLClient.h>
#include <Ice/SslConnectionOpenSSLClient.h>

#include <Ice/TraceLevels.h>
#include <Ice/Logger.h>

#include <iostream>

using IceSSL::ConnectionPtr;
using IceSSL::SystemInternalPtr;

IceSSL::OpenSSL::ClientContext::ClientContext(const IceInternal::InstancePtr& instance) :
                                         Context(instance)
{
    _rsaPrivateKeyProperty = "Ice.SSL.Client.Overrides.RSA.PrivateKey";
    _rsaPublicKeyProperty  = "Ice.SSL.Client.Overrides.RSA.Certificate";
    _dsaPrivateKeyProperty = "Ice.SSL.Client.Overrides.DSA.PrivateKey";
    _dsaPublicKeyProperty  = "Ice.SSL.Client.Overrides.DSA.Certificate";
    _caCertificateProperty = "Ice.SSL.Client.Overrides.CACertificate";
    _handshakeTimeoutProperty = "Ice.SSL.Client.Handshake.ReadTimeout";
}

void
IceSSL::OpenSSL::ClientContext::configure(const GeneralConfig& generalConfig,
                                          const CertificateAuthority& certificateAuthority,
                                          const BaseCertificates& baseCertificates)
{
    Context::configure(generalConfig, certificateAuthority, baseCertificates);

    loadCertificateAuthority(certificateAuthority);

    if (_traceLevels->security >= IceSSL::SECURITY_PROTOCOL)
    {
        std::ostringstream s;

        s << std::endl;
        s << "General Configuration - Client" << std::endl;
        s << "------------------------------" << std::endl;
        s << generalConfig << std::endl << std::endl;

        s << "Certificate Authority - Client" << std::endl;
        s << "------------------------------" << std::endl;
        s << "File: " << certificateAuthority.getCAFileName() << std::endl;
        s << "Path: " << certificateAuthority.getCAPath() << std::endl;

        s << "Base Certificates - Client" << std::endl;
        s << "--------------------------" << std::endl;
        s << baseCertificates << std::endl;

        _logger->trace(_traceLevels->securityCat, s.str());
    }
}

IceSSL::ConnectionPtr
IceSSL::OpenSSL::ClientContext::createConnection(int socket, const SystemInternalPtr& system)
{
    if (_sslContext == 0)
    {
        // ContextNotConfiguredException contextEx(__FILE__, __LINE__);
        IceSSL::OpenSSL::ContextException contextEx(__FILE__, __LINE__);

        contextEx._message = "SSL Context not configured.";

        throw contextEx;
    }

    ConnectionPtr connection = new ClientConnection(_traceLevels,
                                                    _logger,
                                                    _certificateVerifier,
                                                    createSSLConnection(socket),
                                                    system);

    connectionSetup(connection);

    return connection;
}

