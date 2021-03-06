<?xml version="1.0" encoding="ISO-8859-1"?>
<!--
kOLEKTi : a structural documentation generator
Copyright (C) 2007 St�phane Bonhomme (stephane@exselt.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


-->
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
    xmlns:html="http://www.w3.org/1999/xhtml" 
    xmlns:xt="http://ns.inria.org/xtiger"
    xmlns:kf="kolekti:extensions:functions"
    xmlns:kfp="kolekti:extensions:functions:publication"
    extension-element-prefixes="kfp kf"
    exclude-result-prefixes="html kfp kf"
    version="1.0">


  <xsl:variable name="criteria" select="kfp:criteria()"/>

  
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -->

  <!-- template de suppression des pr�dicats XTiger -->
  <xsl:template match="xt:*">	
	<xsl:apply-templates/>
  </xsl:template>
  
  <!-- template de suppression de la div topicinfo -->	
  <!--  	<xsl:template match="html:div[@class='topicinfo']"/>-->


  <!-- ce template produit un booleen 
       vrai si toutes les conditions de listcond sont v�rifi�es -->
  <xsl:template name="process_list_cond">
    <xsl:param name="listcond"/>
    <xsl:choose>
      <xsl:when test="contains($listcond,';')">
        <xsl:variable name="cond_prefix">
          <xsl:call-template name="process_cond">
            <xsl:with-param name="cond" select="substring-before($listcond,';')"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:choose>
          <xsl:when test="$cond_prefix='true'">
            <xsl:call-template name="process_list_cond">
              <xsl:with-param name="listcond" select="substring-after($listcond,';')"/>
            </xsl:call-template>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$cond_prefix"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="process_cond">
          <xsl:with-param name="cond" select="$listcond"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  <!-- ce template produit un booleen 
       vrai si la chaine value est dans la liste  -->
  <xsl:template name="value_in_list">
    <xsl:param name="value"/>
    <xsl:param name="list"/>
    <!--
        <xsl:message><xsl:value-of select="$value"/> in <xsl:value-of select="$list"/>        <xsl:value-of select="$value=$list"/> </xsl:message>
    -->
    
    <xsl:choose>
      <xsl:when test="contains($list,',')">
        <xsl:choose>
          <xsl:when test="$value=substring-before($list,',')">
            <xsl:value-of select="true()"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="value_in_list">
              <xsl:with-param name="value" select="$value"/>
              <xsl:with-param name="list" select="substring-after($list,',')"/>
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$value=$list"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  

  <!-- ce template produit un booleen 
       vrai si la chaine value est un nombre et est compris dans le range [min-max]  -->
  <xsl:template name="value_in_range">
    <xsl:param name="value"/>
    <xsl:param name="range"/>
    <xsl:variable name="min" select="number(substring-after(substring-before($range,'-'),'['))"/>
    <xsl:variable name="max" select="number(substring-before(substring-after($range,'-'),']'))"/>
    <xsl:variable name="val" select="number($value)"/>
    <xsl:value-of select="boolean($val &gt;= $min and $val &lt;= $max)"/>    
  </xsl:template>


  
  <!-- ce template produit une chaine true/false/none/user 
       vrai si la condition cond  est verfiee
       false si elle est sp�cifi�e dans le profil et non v�rifi�e
       user si elle est sp�cifi�e dans le profil sans valeur
       none si elle n'est pas sp�cifi�e dans le profil
  -->
  
  <xsl:template name="process_cond">
    <xsl:param name="cond"/>
    <xsl:variable name="predicat" select="substring-before($cond,'=')"/>
    <xsl:variable name="values">
      <xsl:choose>
        <xsl:when test="starts-with(substring-after($cond,'='),'\')">
          <xsl:value-of select="substring-after(substring-after($cond,'='),'\')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="substring-after($cond,'=')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>


    <xsl:choose>
      
      <xsl:when test="$criteria[@code=$predicat][@value]">
        <!-- le crit�re est sp�cifi� dans le profil et a une valeur -->
        <xsl:variable name="found">
	      <xsl:choose>
	        <xsl:when test="starts-with($values,'[')">
	          <xsl:call-template name="value_in_range">
		        <xsl:with-param name="value" select="$criteria[@code=$predicat]/@value"/>
                <!--
		            <xsl:with-param name="value" select="/html:html/html:head/html:meta[@scheme='condition'][@name=$predicat]/@content"/>
                -->
		        <xsl:with-param name="range" select="$values"/>
	          </xsl:call-template>
	        </xsl:when>
	        <xsl:otherwise>
	          <xsl:call-template name="value_in_list">
                <!--
		            <xsl:with-param name="value" select="/html:html/html:head/html:meta[@scheme='condition'][@name=$predicat]/@content"/>
                -->
		        <xsl:with-param name="value" select="$criteria[@code=$predicat]/@value"/>
		        <xsl:with-param name="list" select="$values"/>
	          </xsl:call-template>
	        </xsl:otherwise>
	      </xsl:choose>
        </xsl:variable>

        <xsl:choose>
          <xsl:when test="starts-with(substring-after($cond,'='),'\')">
            <xsl:choose>
	          <xsl:when test="$found = 'false'">true</xsl:when>
	          <xsl:otherwise>false</xsl:otherwise>
	        </xsl:choose>
          </xsl:when>
          <xsl:otherwise>
            <xsl:choose>
	          <xsl:when test="$found = 'true'">true</xsl:when>
	          <xsl:otherwise>false</xsl:otherwise>
	        </xsl:choose>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <!-- le crit�re est sp�cifi� dans le profil et n'a pas de valeur (user) -->
      <xsl:when test="$criteria[@code=$predicat][not(@value)]">user</xsl:when>

      <!-- le crit�re n'est pas sp�cifi� dans le profil -->
      <xsl:otherwise>none</xsl:otherwise>

    </xsl:choose>

  </xsl:template>

  
</xsl:stylesheet>
