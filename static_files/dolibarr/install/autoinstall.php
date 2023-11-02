<?php
session_start();
include 'inc.php';
require_once '../core/class/conf.class.php';
require_once '../core/lib/admin.lib.php';
require_once '../core/lib/security.lib.php';
require_once '../core/class/hookmanager.class.php';

global $langs;

$err = 0;

$setuplang = "fr_FR";
$langs->setDefaultLang($setuplang);

// Cette page peut etre longue. On augmente le delai autorise.
// Ne fonctionne que si on est pas en safe_mode.
$err = error_reporting();
error_reporting(0); // Disable all errors
//error_reporting(E_ALL);
@set_time_limit(1800); // Need 1800 on some very slow OS like Windows 7/64
error_reporting($err);

$dolibarr_main_db_type = "mysqli";
$dolibarr_main_db_name = "${DOLIBARR_NAME}";
$choix = 1;

//if (empty($choix)) dol_print_error('','Database type '.$dolibarr_main_db_type.' not supported into step2.php page');


//Database creation 

$newdb = getDoliDBInstance("mysqli", "${USER}-db", "root", "root","", 3306);

if ($newdb->connected) {
$result = $newdb->DDLCreateDb($dolibarr_main_db_name, "utf8", "utf8_general_ci", "root");

if ($result) {
	$newdb->select_db($dolibarr_main_db_name);
	$check1 = $newdb->getDefaultCharacterSetDatabase();
	$check2 = $newdb->getDefaultCollationDatabase();
	dolibarr_install_syslog('step1: new database is using charset='.$check1.' collation='.$check2);

	// If values differs, we save conf file again
	//if ($check1 != $dolibarr_main_db_character_set) dolibarr_install_syslog('step1: value for character_set is not the one asked for database creation', LOG_WARNING);
	//if ($check2 != $dolibarr_main_db_collation)     dolibarr_install_syslog('step1: value for collation is not the one asked for database creation', LOG_WARNING);

$newdb->close();
}
else{
	print -1;
}
}




// Now we load forced values from install.forced.php file.
$forcedfile = "./install.forced.php";
include_once $forcedfile;

$db = getDoliDBInstance("mysqli", "${USER}-db", "root", "root", "${DOLIBARR_NAME}", 3306); 
if ($db->connected) {
    print "Database connected !\n";
    $ok = 1;
    $createtables = 1;
	$createkeys = 1;
	$createfunctions = 1;
	$createdata = 1;
    $db->unescapeslashquot = true;

    if ($ok && $createtables) {
		// We always choose in mysql directory (Conversion is done by driver to translate SQL syntax)
		$dir = "mysql/tables/";

		$ok = 0;
		$handle = opendir($dir);
		$tablefound = 0;
		$tabledata = array();
		if (is_resource($handle)) {
			while (($file = readdir($handle)) !== false) {
				if (preg_match('/\.sql$/i', $file) && preg_match('/^llx_/i', $file) && !preg_match('/\.key\.sql$/i', $file) && !preg_match('/\-/', $file)) {
					$tablefound++;
					$tabledata[] = $file;
				}
			}
			closedir($handle);
		}
		// Sort list of sql files on alphabetical order (load order is important)
		sort($tabledata);
		foreach ($tabledata as $file) {
			$name = substr($file, 0, dol_strlen($file) - 4);
			$buffer = '';
			$fp = fopen($dir.$file, "r");
			if ($fp) {
				while (!feof($fp)) {
					$buf = fgets($fp, 4096);
					if (substr($buf, 0, 2) <> '--') {
						$buf = preg_replace('/--(.+)*/', '', $buf);
						$buffer .= $buf;
					}
				}
				fclose($fp);

				$buffer = trim($buffer);
				if ($conf->db->type == 'mysql' || $conf->db->type == 'mysqli') {	// For Mysql 5.5+, we must replace type=innodb with ENGINE=innodb
					$buffer = preg_replace('/type=innodb/i', 'ENGINE=innodb', $buffer);
				} else {
					// Keyword ENGINE is MySQL-specific, so scrub it for
					// other database types (mssql, pgsql)
					$buffer = preg_replace('/type=innodb/i', '', $buffer);
					$buffer = preg_replace('/ENGINE=innodb/i', '', $buffer);
				}

				// Replace the prefix tables
				if ($dolibarr_main_db_prefix != 'llx_') {
					$buffer = preg_replace('/llx_/i', $dolibarr_main_db_prefix, $buffer);
				}

				//print "<tr><td>Creation de la table $name/td>";
				$requestnb++;

				$resql = $db->query($buffer, 0, 'dml');
				if ($resql) {
					// print "<td>OK requete ==== $buffer</td></tr>";
					$db->free($resql);
				} else {
					if ($db->errno() == 'DB_ERROR_TABLE_ALREADY_EXISTS' ||
					$db->errno() == 'DB_ERROR_TABLE_OR_KEY_ALREADY_EXISTS') {
						//print "<td>Deja existante</td></tr>";
					} else {
						print "<tr><td>".$langs->trans("CreateTableAndPrimaryKey", $name);
						print "<br>\n".$langs->trans("Request").' '.$requestnb.' : '.$buffer.' <br>Executed query : '.$db->lastquery;
						print "\n</td>";
						print '<td><span class="error">'.$langs->trans("ErrorSQL")." ".$db->errno()." ".$db->error().'</span></td></tr>';
						$error++;
					}
				}
			} else {
				print "<tr><td>".$langs->trans("CreateTableAndPrimaryKey", $name);
				print "</td>";
				print '<td><span class="error">'.$langs->trans("Error").' Failed to open file '.$dir.$file.'</span></td></tr>';
				$error++;
				dolibarr_install_syslog("step2: failed to open file ".$dir.$file, LOG_ERR);
			}
		}

		if ($tablefound) {
			if ($error == 0) {
				$ok = 1;
			}
		} else {
			print '<tr><td>'.$langs->trans("ErrorFailedToFindSomeFiles", $dir).'</td><td><img src="../theme/eldy/img/error.png" alt="Error"></td></tr>';
			dolibarr_install_syslog("step2: failed to find files to create database in directory ".$dir, LOG_ERR);
		}
	}

    if ($ok && $createfunctions) {
		// For this file, we use a directory according to database type
		if ($choix == 1) {
			$dir = "mysql/functions/";
		} elseif ($choix == 2) {
			$dir = "pgsql/functions/";
		} elseif ($choix == 3) {
			$dir = "mssql/functions/";
		} elseif ($choix == 4) {
			$dir = "sqlite3/functions/";
		}

		// Creation donnees
		$file = "functions.sql";
		if (file_exists($dir.$file)) {
			$fp = fopen($dir.$file, "r");
			dolibarr_install_syslog("step2: open function file ".$dir.$file." handle=".$fp);
			if ($fp) {
				$buffer = '';
				while (!feof($fp)) {
					$buf = fgets($fp, 4096);
					if (substr($buf, 0, 2) <> '--') {
						$buffer .= $buf."§";
					}
				}
				fclose($fp);
			}
			//$buffer=preg_replace('/;\';/',";'§",$buffer);

			// If several requests, we loop on each of them
			$listesql = explode('§', $buffer);
			foreach ($listesql as $buffer) {
				$buffer = trim($buffer);
				if ($buffer) {
					// Replace the prefix in table names
					if ($dolibarr_main_db_prefix != 'llx_') {
						$buffer = preg_replace('/llx_/i', $dolibarr_main_db_prefix, $buffer);
					}
					dolibarr_install_syslog("step2: request: ".$buffer);
					print "<!-- Insert line : ".$buffer."<br>-->\n";
					$resql = $db->query($buffer, 0, 'dml');
					if ($resql) {
						$ok = 1;
						$db->free($resql);
					} else {
						if ($db->errno() == 'DB_ERROR_RECORD_ALREADY_EXISTS'
						|| $db->errno() == 'DB_ERROR_KEY_NAME_ALREADY_EXISTS') {
							//print "Insert line : ".$buffer."<br>\n";
						} else {
							$ok = 0;

							print "<tr><td>".$langs->trans("FunctionsCreation");
							print "<br>\n".$langs->trans("Request").' '.$requestnb.' : '.$buffer;
							print "\n</td>";
							print '<td><span class="error">'.$langs->trans("ErrorSQL")." ".$db->errno()." ".$db->error().'</span></td></tr>';
							$error++;
						}
					}
				}
			}

			//print "<tr><td>".$langs->trans("FunctionsCreation")."</td>";
		}
	}

    if ($ok && $createkeys) {
		// We always choose in mysql directory (Conversion is done by driver to translate SQL syntax)
		$dir = "mysql/tables/";

		$okkeys = 0;
		$handle = opendir($dir);
		dolibarr_install_syslog("step2: open keys directory ".$dir." handle=".$handle);
		$tablefound = 0;
		$tabledata = array();
		if (is_resource($handle)) {
			while (($file = readdir($handle)) !== false) {
				if (preg_match('/\.sql$/i', $file) && preg_match('/^llx_/i', $file) && preg_match('/\.key\.sql$/i', $file) && !preg_match('/\-/', $file)) {
					$tablefound++;
					$tabledata[] = $file;
				}
			}
			closedir($handle);
		}

		// Sort list of sql files on alphabetical order (load order is important)
		sort($tabledata);
		foreach ($tabledata as $file) {
			$name = substr($file, 0, dol_strlen($file) - 4);
			//print "<tr><td>Creation de la table $name</td>";
			$buffer = '';
			$fp = fopen($dir.$file, "r");
			if ($fp) {
				while (!feof($fp)) {
					$buf = fgets($fp, 4096);

					// Special case of lines allowed for some version only
					if ($choix == 1 && preg_match('/^--\sV([0-9\.]+)/i', $buf, $reg)) {
						$versioncommande = explode('.', $reg[1]);
						//print var_dump($versioncommande);
						//print var_dump($versionarray);
						if (count((array)$versioncommande) && count((array)$versionarray)
						&& versioncompare($versioncommande, $versionarray) <= 0) {
							// Version qualified, delete SQL comments
							$buf = preg_replace('/^--\sV([0-9\.]+)/i', '', $buf);
							//print "Ligne $i qualifiee par version: ".$buf.'<br>';
						}
					}
					if ($choix == 2 && preg_match('/^--\sPOSTGRESQL\sV([0-9\.]+)/i', $buf, $reg)) {
						$versioncommande = explode('.', $reg[1]);
						//print var_dump($versioncommande);
						//print var_dump($versionarray);
						if (count($versioncommande) && count($versionarray)
						&& versioncompare($versioncommande, $versionarray) <= 0) {
							// Version qualified, delete SQL comments
							$buf = preg_replace('/^--\sPOSTGRESQL\sV([0-9\.]+)/i', '', $buf);
							//print "Ligne $i qualifiee par version: ".$buf.'<br>';
						}
					}

					// Ajout ligne si non commentaire
					if (!preg_match('/^--/i', $buf)) {
						$buffer .= $buf;
					}
				}
				fclose($fp);

				// Si plusieurs requetes, on boucle sur chaque
				$listesql = explode(';', $buffer);
				foreach ($listesql as $req) {
					$buffer = trim($req);
					if ($buffer) {
						// Replace the prefix tables
						if ($dolibarr_main_db_prefix != 'llx_') {
							$buffer = preg_replace('/llx_/i', $dolibarr_main_db_prefix, $buffer);
						}

						//print "<tr><td>Creation des cles et index de la table $name: '$buffer'</td>";
						$requestnb++;

						dolibarr_install_syslog("step2: request: ".$buffer);
						$resql = $db->query($buffer, 0, 'dml');
						if ($resql) {
							//print "<td>OK requete ==== $buffer</td></tr>";
							$db->free($resql);
						} else {
							if ($db->errno() == 'DB_ERROR_KEY_NAME_ALREADY_EXISTS' ||
							$db->errno() == 'DB_ERROR_CANNOT_CREATE' ||
							$db->errno() == 'DB_ERROR_PRIMARY_KEY_ALREADY_EXISTS' ||
							$db->errno() == 'DB_ERROR_TABLE_OR_KEY_ALREADY_EXISTS' ||
							preg_match('/duplicate key name/i', $db->error())) {
								//print "<td>Deja existante</td></tr>";
								$key_exists = 1;
							} else {
								print "<tr><td>".$langs->trans("CreateOtherKeysForTable", $name);
								print "<br>\n".$langs->trans("Request").' '.$requestnb.' : '.$db->lastqueryerror();
								print "\n</td>";
								print '<td><span class="error">'.$langs->trans("ErrorSQL")." ".$db->errno()." ".$db->error().'</span></td></tr>';
								$error++;
							}
						}
					}
				}
			} else {
				print "<tr><td>".$langs->trans("CreateOtherKeysForTable", $name);
				print "</td>";
				print '<td><span class="error">'.$langs->trans("Error")." Failed to open file ".$dir.$file."</span></td></tr>";
				$error++;
				dolibarr_install_syslog("step2: failed to open file ".$dir.$file, LOG_ERR);
			}
		}

		if ($tablefound && $error == 0) {
			$okkeys = 1;
		}
	}

    if ($ok && $createdata) {
		// We always choose in mysql directory (Conversion is done by driver to translate SQL syntax)
		$dir = "mysql/data/";

		// Insert data
		$handle = opendir($dir);
		dolibarr_install_syslog("step2: open directory data ".$dir." handle=".$handle);
		$tablefound = 0;
		$tabledata = array();
		if (is_resource($handle)) {
			while (($file = readdir($handle)) !== false) {
				if (preg_match('/\.sql$/i', $file) && preg_match('/^llx_/i', $file) && !preg_match('/\-/', $file)) {
					if (preg_match('/^llx_accounting_account_/', $file)) {
						continue; // We discard data file of chart of account. Will be loaded when a chart is selected.
					}

					//print 'x'.$file.'-'.$createdata.'<br>';
					if (is_numeric($createdata) || preg_match('/'.preg_quote($createdata).'/i', $file)) {
						$tablefound++;
						$tabledata[] = $file;
					}
				}
			}
			closedir($handle);
		}

		// Sort list of data files on alphabetical order (load order is important)
		sort($tabledata);
		foreach ($tabledata as $file) {
			$name = substr($file, 0, dol_strlen($file) - 4);
			$fp = fopen($dir.$file, "r");
			dolibarr_install_syslog("step2: open data file ".$dir.$file." handle=".$fp);
			if ($fp) {
				$arrayofrequests = array();
				$linefound = 0;
				$linegroup = 0;
				$sizeofgroup = 1; // Grouping request to have 1 query for several requests does not works with mysql, so we use 1.

				// Load all requests
				while (!feof($fp)) {
					$buffer = fgets($fp, 4096);
					$buffer = trim($buffer);
					if ($buffer) {
						if (substr($buffer, 0, 2) == '--') {
							continue;
						}

						if ($linefound && ($linefound % $sizeofgroup) == 0) {
							$linegroup++;
						}
						if (empty($arrayofrequests[$linegroup])) {
							$arrayofrequests[$linegroup] = $buffer;
						} else {
							$arrayofrequests[$linegroup] .= " ".$buffer;
						}

						$linefound++;
					}
				}
				fclose($fp);

				dolibarr_install_syslog("step2: found ".$linefound." records, defined ".count($arrayofrequests)." group(s).");

				$okallfile = 1;
				$db->begin();

				// We loop on each requests of file
				foreach ($arrayofrequests as $buffer) {
					// Replace the prefix tables
					if ($dolibarr_main_db_prefix != 'llx_') {
						$buffer = preg_replace('/llx_/i', $dolibarr_main_db_prefix, $buffer);
					}

					//dolibarr_install_syslog("step2: request: " . $buffer);
					$resql = $db->query($buffer, 1);
					if ($resql) {
						//$db->free($resql);     // Not required as request we launch here does not return memory needs.
					} else {
						if ($db->lasterrno() == 'DB_ERROR_RECORD_ALREADY_EXISTS') {
							//print "<tr><td>Insertion ligne : $buffer</td><td>";
						} else {
							$ok = 0;
							$okallfile = 0;
							print '<span class="error">'.$langs->trans("ErrorSQL")." : ".$db->lasterrno()." - ".$db->lastqueryerror()." - ".$db->lasterror()."</span><br>";
						}
					}
				}

				if ($okallfile) {
					$db->commit();
				} else {
					$db->rollback();
				}
			}
		}

		//print "<tr><td>".$langs->trans("ReferenceDataLoading")."</td>";
		if (!$ok) {
			$ok = 1; // Data loading are not blocking errors
		}
	}


    $modName = 'modUser';
    $file = $modName.".class.php";
    include_once DOL_DOCUMENT_ROOT."/core/modules/".$file;
    $objMod = new $modName($db);
    $result = $objMod->init();     
    $conf->global->MAIN_ENABLE_LOG_TO_HTML = 1;

	// Create admin user
	include_once DOL_DOCUMENT_ROOT.'/user/class/user.class.php';

	// Create user used to create the admin user
	$createuser = new User($db);
	$createuser->id = 0;
	$createuser->admin = 1;

	// Set admin user
	$newuser = new User($db);
	$newuser->lastname = 'SuperAdmin';
	$newuser->firstname = '';
	$newuser->login = "admin";
	$newuser->pass = "admin";
	$newuser->admin = 1;
	$newuser->entity = 0;

	$conf->global->USER_MAIL_REQUIRED = 0; 			// Force global option to be sure to create a new user with no email
	$conf->global->USER_PASSWORD_GENERATED = '';	// To not use any rule for password validation

	$success = 0;
	$result = $newuser->create($createuser, 1);
	if ($result > 0) {
		$success = 1;
	} 

	if($success){
		if ($success) {
			// Insert MAIN_VERSION_FIRST_INSTALL in a dedicated transaction. So if it fails (when first install was already done), we can do other following requests.
			$db->begin();
			dolibarr_install_syslog('step5: set MAIN_VERSION_FIRST_INSTALL const to '.$targetversion, LOG_DEBUG);
			$resql = $db->query("INSERT INTO ".MAIN_DB_PREFIX."const(name,value,type,visible,note,entity) values(".$db->encrypt('MAIN_VERSION_FIRST_INSTALL', 1).",".$db->encrypt($targetversion, 1).",'chaine',0,'Dolibarr version when first install',0)");
			if ($resql) {
				$conf->global->MAIN_VERSION_FIRST_INSTALL = $targetversion;
				$db->commit();
			} else {
				//if (! $resql) dol_print_error($db,'Error in setup program');      // We ignore errors. Key may already exists
				$db->commit();
			}

			$db->begin();

			dolibarr_install_syslog('step5: set MAIN_VERSION_LAST_INSTALL const to '.$targetversion, LOG_DEBUG);
			$resql = $db->query("DELETE FROM ".MAIN_DB_PREFIX."const WHERE ".$db->decrypt('name')."='MAIN_VERSION_LAST_INSTALL'");
			if (!$resql) {
				dol_print_error($db, 'Error in setup program');
			}
			$resql = $db->query("INSERT INTO ".MAIN_DB_PREFIX."const(name,value,type,visible,note,entity) values(".$db->encrypt('MAIN_VERSION_LAST_INSTALL', 1).",".$db->encrypt($targetversion, 1).",'chaine',0,'Dolibarr version when last install',0)");
			if (!$resql) {
				dol_print_error($db, 'Error in setup program');
			}
			$conf->global->MAIN_VERSION_LAST_INSTALL = $targetversion;

			if ($useforcedwizard) {
				dolibarr_install_syslog('step5: set MAIN_REMOVE_INSTALL_WARNING const to 1', LOG_DEBUG);
				$resql = $db->query("DELETE FROM ".MAIN_DB_PREFIX."const WHERE ".$db->decrypt('name')."='MAIN_REMOVE_INSTALL_WARNING'");
				if (!$resql) {
					dol_print_error($db, 'Error in setup program');
				}
				$resql = $db->query("INSERT INTO ".MAIN_DB_PREFIX."const(name,value,type,visible,note,entity) values(".$db->encrypt('MAIN_REMOVE_INSTALL_WARNING', 1).",".$db->encrypt(1, 1).",'chaine',1,'Disable install warnings',0)");
				if (!$resql) {
					dol_print_error($db, 'Error in setup program');
				}
				$conf->global->MAIN_REMOVE_INSTALL_WARNING = 1;
			}

			// If we ask to force some modules to be enabled
			if (!empty($force_install_module)) {
				if (!defined('DOL_DOCUMENT_ROOT') && !empty($dolibarr_main_document_root)) {
					define('DOL_DOCUMENT_ROOT', $dolibarr_main_document_root);
				}

				$tmparray = explode(',', $force_install_module);
				foreach ($tmparray as $modtoactivate) {
					$modtoactivatenew = preg_replace('/\.class\.php$/i', '', $modtoactivate);
					print $langs->trans("ActivateModule", $modtoactivatenew).'<br>';

					$file = $modtoactivatenew.'.class.php';
					dolibarr_install_syslog('step5: activate module file='.$file);
					$res = dol_include_once("/core/modules/".$file);

					$res = activateModule($modtoactivatenew, 1);
					if (!empty($res['errors'])) {
						print 'ERROR in activating module file='.$file;
					}
				}
			}

			dolibarr_install_syslog('step5: remove MAIN_NOT_INSTALLED const');
			$resql = $db->query("DELETE FROM ".MAIN_DB_PREFIX."const WHERE ".$db->decrypt('name')."='MAIN_NOT_INSTALLED'");
			if (!$resql) {
				dol_print_error($db, 'Error in setup program');
			}
			dolibarr_set_const($db, "MAIN_LANG_DEFAULT", $setuplang, 'chaine', 0, '', $conf->entity); 

			$db->commit();
			print 1;
		}
	}


} 