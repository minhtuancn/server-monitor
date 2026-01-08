# Software Bill of Materials (SBOM)

This directory contains Software Bill of Materials (SBOM) files for the Server Monitor project in CycloneDX format.

## Files

- **sbom-python.json** - Python backend dependencies
- **sbom-node.json** - Node.js frontend dependencies

## What is SBOM?

A Software Bill of Materials (SBOM) is a comprehensive inventory of all components, libraries, and dependencies used in a software project. It provides transparency into the software supply chain and helps:

- **Security**: Quickly identify vulnerable components
- **Compliance**: Verify license compliance
- **Transparency**: Provide visibility into dependencies
- **Risk Management**: Assess supply chain risks

## Format

These SBOMs use the [CycloneDX](https://cyclonedx.org/) standard version 1.4, which is:
- Machine-readable
- Industry standard
- Supported by security tools
- Compatible with vulnerability databases

## Using SBOM Files

### Verify Components

```bash
# View Python dependencies
cat sbom-python.json | jq '.components[].name'

# View Node.js dependencies
cat sbom-node.json | jq '.components[].name'
```

### Security Scanning

Use SBOM with security tools:

```bash
# With Grype (vulnerability scanner)
grype sbom:sbom-python.json

# With OSS Index
curl -X POST -H "Content-Type: application/json" \
  --data @sbom-python.json \
  https://ossindex.sonatype.org/api/v3/component-report
```

### License Compliance

Extract license information:

```bash
# List all components with licenses
cat sbom-python.json | jq '.components[] | {name, version, licenses}'
```

## Generating SBOMs

### Python (Automated)

```bash
# Install cyclonedx-bom
pip install cyclonedx-bom

# Generate SBOM from requirements.txt
cyclonedx-py requirements backend/requirements.txt -o sbom-python.json
```

### Node.js (Automated)

```bash
# Install cyclonedx npm plugin
npm install -g @cyclonedx/cyclonedx-npm

# Generate SBOM from package-lock.json
cd frontend-next
cyclonedx-npm --output-file sbom-node.json
```

## Versioning

SBOMs should be regenerated:
- With each release
- When dependencies are updated
- For security audits
- For compliance reviews

Current version corresponds to: **v2.2.0**

## Standards Compliance

These SBOMs comply with:
- [CycloneDX Specification 1.4](https://cyclonedx.org/specification/overview/)
- [NTIA Minimum Elements for SBOM](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom)
- [Executive Order 14028](https://www.nist.gov/itl/executive-order-14028-improving-nations-cybersecurity) (Improving the Nation's Cybersecurity)

## Related Documentation

- [Security Scanning Guide](../SECURITY_SCANNING.md)
- [Release Process](../RELEASE_PROCESS.md)
- [Security Policy](../../SECURITY.md)

## Contact

For questions about SBOMs or supply chain security, contact the DevSecOps team.
