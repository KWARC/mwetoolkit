<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */
// +----------------------------------------------------------------------+
// | TemplatePower:                                                       |
// | offers you the ability to separate your PHP code and your HTML       |
// +----------------------------------------------------------------------+
// |                                                                      |
// | Copyright (C) 2001  R.P.J. Velzeboer, The Netherlands                |
// |                                                                      |
// | This program is free software; you can redistribute it and/or        |
// | modify it under the terms of the GNU General Public License          |
// | as published by the Free Software Foundation; either version 2       |
// | of the License, or (at your option) any later version.               |
// |                                                                      |
// | This program is distributed in the hope that it will be useful,      |
// | but WITHOUT ANY WARRANTY; without even the implied warranty of       |
// | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        |
// | GNU General Public License for more details.                         |
// |                                                                      |
// | You should have received a copy of the GNU General Public License    |
// | along with this program; if not, write to the Free Software          |
// | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA            |
// | 02111-1307, USA.                                                     |
// |                                                                      |
// | Author: R.P.J. Velzeboer, rovel@codocad.nl   The Netherlands         |
// |                                                                      |
// +----------------------------------------------------------------------+
// | http://templatepower.codocad.com                                     |
// +----------------------------------------------------------------------+
//
// $Id: Version 2.0 beta-e$


class TemplatePowerParser
{
  var $tpl_mainfile;
  var $tpl_includefile;
  var $tpl_count;

  var $parent   = Array();        // $parent[{blockname}] = {parentblockname}
  var $defBlock = Array();        // empty block, just the defenition of the block

  var $rootBlockName;

   function TemplatePowerParser( $tpl_file )
   {
       $this->rootBlockName  = '_ROOT';
       $this->tpl_mainfile   = $tpl_file;
       $this->tpl_count      = 0;
   }

   function prepare()
   {
        $this->defBlock[ $this->rootBlockName ] = Array();
        $tplvar = TemplatePower::prepareTemplate( $this->tpl_mainfile );

        $initdev["varrow"]  = 0;
        $initdev["coderow"] = 0;
        $initdev["index"]   = 0;
        $initdev["ignore"]  = false;

        TemplatePower::parseTemplate( $tplvar, $this->rootBlockName, $initdev );
        TemplatePower::cleanUp();
    }

    function cleanUp()
    {
        for( $i=0; $i <= $this->tpl_count; $i++ )
        {
            $tplvar = 'tpl_rawContent'. $i;
            unset( $this->{$tplvar} );
        }
    }

    function assignInclude( $iblockname, $value )
    {
        $this->tpl_includefile["$iblockname"] = $value;
    }

    function prepareTemplate( $tpl_file )
    {
        $tplvar = 'tpl_rawContent'. $this->tpl_count;
        $this->{$tplvar}["content"] = @file( $tpl_file ) or die( $this->errorAlert("TemplatePower Error: Couldn't open [ $tpl_file ]!"));
        $this->{$tplvar}["size"]    = sizeof( $this->{$tplvar}["content"] );

        $this->tpl_count++;

        return $tplvar;
    }

    function parseTemplate( $tplvar, $blockname, $initdev )
    {
        $coderow = $initdev["coderow"];
        $varrow  = $initdev["varrow"];
        $index   = $initdev["index"];
        $ignore  = $initdev["ignore"];

        while( $index < $this->{$tplvar}["size"] )
        {
            if ( preg_match("/<!--[ ]?(START|END) IGNORE -->/", $this->{$tplvar}["content"][$index], $ignreg) )
            {
                if( $ignreg[1] == "START")
                {
                    $ignore = true;
                }
                else
                {
                    $ignore = false;
                }
            }
            else
            {
                if( $ignore == false )
                {
                    if( preg_match("/<!--[ ]?(START|END|INCLUDE|INCLUDESCRIPT|REUSE) BLOCK : (.+)-->/", $this->{$tplvar}["content"][$index], $regs))
                    {
                       //remove trailing and leading spaces
                        $regs[2] = trim( $regs[2] );

                        if( $regs[1] == "INCLUDE")
                        {
                           //check if the include file is assigned by the assignInclude function
                            if( isset( $this->tpl_includefile[ $regs[2] ]) )
                            {
                               //initialize startvalues for recursive call
                                $initdev["varrow"]  = $varrow;
                                $initdev["coderow"] = $coderow;
                                $initdev["index"]   = 0;
                                $initdev["ignore"]  = false;

                                $tplvar2 = TemplatePower::prepareTemplate( $this->tpl_includefile[ $regs[2] ] );
                                $initdev = TemplatePower::parseTemplate( $tplvar2, $blockname, $initdev );

                                $coderow = $initdev["coderow"];
                                $varrow  = $initdev["varrow"];
                            }
                        }
                        else
                        if( $regs[1] == "INCLUDESCRIPT" )
                        {
                           //check if the includescript file is assigned by the assignInclude function
                            if( isset( $this->tpl_includefile[ $regs[2] ]) )
                            {
                               //start outputbuffering
                                ob_start();

                               //the output of the include_once function will be captured in the buffer
                                include_once( $this->tpl_includefile[ $regs[2] ] );

                               //store the buffer in the template
                                $this->defBlock[$blockname]["_C:$coderow"] = ob_get_contents();
                                $coderow++;

                               //clean the buffer
                                ob_end_clean();
                            }
                        }
                        else
                        if( $regs[1] == "REUSE" )
                        {
                           //do match for 'AS'
                            if (preg_match("/(.+) AS (.+)/", $regs[2], $reuse_regs))
                            {
                                $originalbname = trim( $reuse_regs[1] );
                                $copybname     = trim( $reuse_regs[2] );

                               //test if original block exist
                                if (isset( $this->defBlock[ $originalbname ] ))
                                {
                                   //copy block
                                    $this->defBlock[ $copybname ] = $this->defBlock[ $originalbname ];

                                   //tell the parent that he has a child block
                                    $this->defBlock[ $blockname ]["_B:". $copybname ] = '';

                                   //create index and parent info
                                    $this->index[ $copybname ]  = 0;
                                    $this->parent[ $copybname ] = $blockname;
                                }
                            }
                            else
                            {
                               //so it isn't a correct REUSE tag, save as code
                               //not really the way to do it, should test it on vars first, but what the hack :-P
                               //maybee in a future release
                                $this->defBlock[$blockname]["_C:$coderow"] = $this->{$tplvar}["content"][$index];
                                $coderow++;
                            }
                        }
                        else
                        {
                            if( $regs[2] == $blockname )     //is it the end of a block
                            {
                                break;                       //end the while loop
                            }
                            else                             //its the start of a block
                            {
                               //make a child block and tell the parent that he has a child
                                $this->defBlock[ $regs[2] ] = Array();
                                $this->defBlock[ $blockname ]["_B:". $regs[2]] = '';

                               //set some vars that we need for the assign functions etc.
                                $this->index[ $regs[2] ]  = 0;
                                $this->parent[ $regs[2] ] = $blockname;

                               //prepare for the recursive call
                                $index++;
                                $initdev["varrow"]  = 0;
                                $initdev["coderow"] = 0;
                                $initdev["index"]   = $index;
                                $initdev["ignore"]  = false;

                                $initdev = TemplatePower::parseTemplate( $tplvar, $regs[2], $initdev );

                                $index = $initdev["index"];
                            }
                        }
                    }
                    else                                                        //is it code and/or var(s)
                    {
                       //explode current template line on the curly bracket '{'
                        $sstr = explode( "{", $this->{$tplvar}["content"][$index] );

                        reset( $sstr );

                        if (current($sstr) != '')
                        {
                           //the template didn't start with a '{',
                           //so the first element of the array $sstr is just code
                            $this->defBlock[$blockname]["_C:$coderow"] = current( $sstr );
                            $coderow++;
                        }

                        $sstrlength = sizeof( $sstr );

                        for ( $i=1; $i < $sstrlength; $i++)
                        {
                            next($sstr);

                           //find the position of the end curly bracket '}'
                            $pos = strpos( current($sstr), "}" );

                            if ( ($pos !== false) && ($pos > 0) )
                            {
                              //it seems that the end curly bracket '}' is found
                              //and at least on position 1, to eliminate '{}' (empty var = no var)
                              //
                              //note: position 1 taken without the '{', because we did explode on '{'

                                $strlength = strlen( current($sstr) );
                                $varname   = substr( current($sstr), 0, $pos );

                               //test varname on spaces
                                if (strstr( $varname, ' ' ))
                                {
                                   //it seems that the varname contains at least one white space
                                   //so, it isn't a variable, we can save it as code
                                    $this->defBlock[$blockname]["_C:$coderow"] = '{'. current( $sstr );
                                    $coderow++;
                                }
                                else
                                {
                                   //save the variable
                                    $this->defBlock[$blockname]["_V:$varrow" ] = $varname;
                                    $varrow++;

                                   //is there some code after the varname left?
                                    if( ($pos + 1) != $strlength )
                                    {
                                       //yes there is, save that code
                                        $this->defBlock[$blockname]["_C:$coderow"] = substr( current( $sstr ), ($pos + 1), ($strlength - ($pos + 1)) );
                                        $coderow++;
                                    }
                                }
                            }
                            else
                            {
                               //no end curly bracket '}' found
                               //so, the curly bracket is part of the text (example: javascript function)
                               //save it as code, with the '{'
                                $this->defBlock[$blockname]["_C:$coderow"] = '{'. current( $sstr );
                                $coderow++;
                            }
                        }
                    }
                }
                else
                {
                    $this->defBlock[$blockname]["_C:$coderow"] = $this->{$tplvar}["content"][$index];
                    $coderow++;
                }
            }

            $index++;
        }

        $initdev["varrow"]  = $varrow;
        $initdev["coderow"] = $coderow;
        $initdev["index"]   = $index;

        return $initdev;
    }
}

class TemplatePower extends TemplatePowerParser
{
  var $index    = Array();        // $index[{blockname}]  = {indexnumber}
  var $content  = Array();        // slightly different structure than $block,
                                  // but than filled with content

  var $currentBlock;
  var $showUnAssigned;
  var $serialized;
  var $globalvars = Array();

    function TemplatePower( $tpl_file, $serialized=false )
    {
        $this->serialized = $serialized;

        TemplatePowerParser::TemplatePowerParser( $tpl_file );

        if ( $this->serialized )
        {
            TemplatePower::deSerializeTPL( $tpl_file );
        }

        $this->showUnAssigned = false;
    }

    function deSerializeTPL( $stpl_file )
    {
        $serializedTPL = @file( $stpl_file ) or die( $this->errorAlert("TemplatePower Error: Couldn't open [ $stpl_file ]!"));
        $serializedStuff = unserialize( join ('', $serializedTPL) );
        //var_dump( $serializedStuff );

        $this->defBlock = $serializedStuff["defBlock"];
        $this->index    = $serializedStuff["index"];
        $this->parent   = $serializedStuff["parent"];
    }

    function showUnAssigned( $state = true )
    {
        $this->showUnAssigned = $state;
    }

    function makeContentRoot()
    {
        $this->content[ $this->rootBlockName ."_0"  ][0] = Array( $this->rootBlockName );
        $this->currentBlock = &$this->content[ $this->rootBlockName ."_0" ][0];
    }

    function prepare()
    {
        if (!$this->serialized)
        {
            TemplatePowerParser::prepare();
        }

        $this->index[ $this->rootBlockName ]    = 0;
        TemplatePower::makeContentRoot();
    }

    function newBlock( $blockname )
    {
        $parent = &$this->content[ $this->parent[$blockname] ."_". $this->index[$this->parent[$blockname]] ];

        if( sizeof($parent) > 1 )
        {
            $lastitem = sizeof( $parent )-1;
        }
        else $lastitem = 0;

        if ( !isset( $parent[ $lastitem ]["_B:$blockname"] ))
        {
           //ok, there is no block found in the parentblock with the name of {$blockname}

           //so, increase the index counter and create a new {$blockname} block
            $this->index[ $blockname ] += 1;

            if (!isset( $this->content[ $blockname ."_". $this->index[ $blockname ] ] ) )
            {
                 $this->content[ $blockname ."_". $this->index[ $blockname ] ] = Array();
            }

           //tell the parent where his (possible) children are located
            $parent[ $lastitem ]["_B:$blockname"] = $blockname ."_". $this->index[ $blockname ];
        }

       //now, make a copy of the block defenition
        $blocksize = sizeof( $this->content[$blockname ."_". $this->index[ $blockname ]] );

        $this->content[ $blockname ."_". $this->index[ $blockname ] ][ $blocksize ] = Array( $blockname );

       //link the current block to the block we just created
        $this->currentBlock = &$this->content[ $blockname ."_". $this->index[ $blockname ] ][ $blocksize ];
    }

    function assignGlobal( $varname, $value )
    {
        $this->globalvars[ $varname ] = $value;
    }

    function assign( $varname, $value )
    {
       //filter block and varname out of $varname string in case of "blockname.varname"
       // if ( preg_match("/(.*)\.(.*)/", $varname, $regs ))

        if( sizeof( $regs = explode(".", $varname ) ) == 2 )  //this is faster then preg_match
        {
            //$blockSize = @key( end( $this->content[ $regs[1] ."_". $this->index[$regs[1]] ] ) );

            $lastitem = sizeof( $this->content[ $regs[0] ."_". $this->index[$regs[0]] ] );

            $lastitem > 1 ? $lastitem-- : $lastitem = 0;

            $block = &$this->content[ $regs[0] ."_". $this->index[ $regs[0] ] ][$lastitem];
            $varname = $regs[1];
        }
        else
        {
            $block = &$this->currentBlock;
        }

        $block["_V:$varname"] = $value;
    }


    function gotoBlock( $blockname )
    {
        if ( isset( $this->defBlock[ $blockname ] ) )
        {
           //get lastitem indexnumber
            $lastitem = sizeof( $this->content[$blockname ."_". $this->index[ $blockname ]] );

            $lastitem > 1 ? $lastitem-- : $lastitem = 0;

           //link the current block
            $this->currentBlock = &$this->content[ $blockname ."_". $this->index[ $blockname ] ][ $lastitem ];
        }
    }

    function getVarValue( $varname )
    {
       //filter block and varname out of $varname string in case of "blockname.varname"
       //if ( preg_match("/(.*)\.(.*)/", $varname, $regs ))

        if( sizeof( $regs = explode(".", $varname ) ) == 2 )  //this is faster then preg_match
        {
            $lastitem = sizeof( $this->content[ $regs[0] ."_". $this->index[$regs[0]] ] );

            $lastitem > 1 ? $lastitem-- : $lastitem = 0;

            $block = &$this->content[ $regs[0] ."_". $this->index[ $regs[0] ] ][$lastitem];
            $varname = $regs[1];
        }
        else
        {
            $block = &$this->currentBlock;
        }

        return $block["_V:$varname"];
    }

    function outputContent( $blockname )
    {
        $numrows = sizeof( $this->content[ $blockname ] );

        for( $i=0; $i < $numrows; $i++)
        {
            $defblockname = $this->content[ $blockname ][$i][0];

            for( reset( $this->defBlock[ $defblockname ]);  $k = key( $this->defBlock[ $defblockname ]);  next( $this->defBlock[ $defblockname ] ) )
            {
                if( preg_match("/C:/", $k) )
                {
                    print( $this->defBlock[ $defblockname ][$k] );
                }
                else
                if( preg_match("/V:/", $k) )
                {
                    $defValue = $this->defBlock[ $defblockname ][$k];

                    if( !isset( $this->content[ $blockname ][$i][ "_V:". $defValue ] ) )
                    {
                        if( isset( $this->globalvars[ $defValue ] ) )
                        {
                            $value = $this->globalvars[ $defValue ];
                        }
                        else
                        {
                            if( $this->showUnAssigned )
                            {
                                //$value = '{'. $this->defBlock[ $defblockname ][$k] .'}';
                                $value = '{'. $defValue .'}';
                            }
                            else
                            {
                                $value = '';
                            }
                        }
                    }
                    else
                    {
                        $value = $this->content[ $blockname ][$i][ "_V:". $defValue ];
                    }

                    print( $value );

                }
                else
                if ( preg_match("/B:/", $k) )
                {
                    if( isset( $this->content[ $blockname ][$i][$k] ) )
                    {
                        TemplatePower::outputContent( $this->content[ $blockname ][$i][$k] );
                    }
                }
            }
        }
    }

    function printToScreen()
    {
        TemplatePower::outputContent( $this->rootBlockName ."_0" );
    }

    function getOutputContent()
    {
       //start outputbuffering
        ob_start();

       //print template, output will be catched in the buffer
        TemplatePower::printToScreen();

       //get buffercontent
        $content = ob_get_contents();

       //clean the buffer
        ob_end_clean();

        return $content;
    }

    function errorAlert( $message )
    {
        print( $message ."<br>");
    }

    function printVars()
    {
        var_dump($this->defBlock);
        print("<br>--------------------<br>");
        var_dump($this->content);
    }
}

class TPLSerializer extends TemplatePowerParser
{
  var $stpl_file;

    function TPLSerializer( $tpl_file, $stpl_file )
    {
        $this->stpl_file = $stpl_file;

        TemplatePowerParser::TemplatePowerParser( $tpl_file );
    }

    function doSerialize()
    {
        TemplatePowerParser::prepare();
        TPLSerializer::serializeTPL();
    }

    function serializeTPL()
    {
        $fp = @fopen( $this->stpl_file, "w")  or die( $this->errorAlert("TemplatePower Error: Couldn't write [ ". $this->stpl_file  ."] for serializing!") );

        $stuffToSerialize = Array( defBlock => $this->defBlock, index => $this->index, parent => $this->parent );

        fputs(  $fp, serialize($stuffToSerialize) );
        fclose( $fp );
        chmod(  $this->stpl_file, 0777 );
    }
}

?>