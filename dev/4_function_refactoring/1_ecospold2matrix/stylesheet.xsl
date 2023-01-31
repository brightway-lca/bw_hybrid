<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/*">
        <root>
            <xsl:apply-templates select="intermediateExchange"/>
        </root>
    </xsl:template>
    <xsl:template match="intermediateExchange">
        <xsl:for-each select="*">
            <xsl:element name="{local-name()}">
                <xsl:value-of select="."/>
            </xsl:element>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
