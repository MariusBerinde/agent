import os
import unittest
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.lynis import Lynis
class TestLynis(unittest.TestCase):
    """
    Test unitari per la classe Lynis.
    """
    def setUp(self):
        """Prepara l'ambiente di test creando un file di profilo temporaneo."""
        self.test_profile = "test_profile.prt"
        with open(self.test_profile, "w") as f:
            f.write("# Test profile for Lynis\n")
            f.write("skip-test=TEST-001\n")
            f.write("skip-test=TEST-002\n")
            f.write("some-other-setting=value\n")
        
        self.lynis = Lynis(self.test_profile)
    
    def tearDown(self):
        """Pulisce l'ambiente di test rimuovendo il file temporaneo."""
        if os.path.exists(self.test_profile):
            os.remove(self.test_profile)
    
    def test_read_skipped_list(self):
        """Verifica che le regole vengano lette correttamente."""
        skipped = self.lynis.read_skipped_list()
        self.assertEqual(len(skipped), 2)
        self.assertIn("TEST-001", skipped)
        self.assertIn("TEST-002", skipped)
    
    def test_delete_rule(self):
        """Verifica che le regole vengano eliminate correttamente."""
        result = self.lynis.delete_rule("TEST-001")
        self.assertTrue(result)
        skipped = self.lynis.read_skipped_list()
        self.assertEqual(len(skipped), 1)
        self.assertNotIn("TEST-001", skipped)
    
    def test_delete_nonexistent_rule(self):
        """Verifica il comportamento quando si elimina una regola inesistente."""
        result = self.lynis.delete_rule("NON-EXISTENT")
        self.assertFalse(result)
        skipped = self.lynis.read_skipped_list()
        self.assertEqual(len(skipped), 2)
    
    def test_add_rules(self):
        """Verifica che le regole vengano aggiunte correttamente."""
        success, added = self.lynis.add_rules(["TEST-003", "TEST-004"])
        self.assertTrue(success)
        self.assertEqual(len(added), 2)
        skipped = self.lynis.read_skipped_list()
        self.assertEqual(len(skipped), 4)
        self.assertIn("TEST-003", skipped)
        self.assertIn("TEST-004", skipped)
    
    def test_add_duplicate_rule(self):
        """Verifica che le regole duplicate non vengano aggiunte."""
        # Prima aggiungiamo una regola
        self.lynis.add_rules(["TEST-003"])
        # Poi proviamo ad aggiungerla di nuovo
        success, added = self.lynis.add_rules(["TEST-003"])
        self.assertFalse(success)  # Non dovrebbero essere state aggiunte regole
        self.assertEqual(len(added), 0)
        skipped = self.lynis.read_skipped_list()
        # Dovremmo avere solo 3 regole (le 2 originali + quella aggiunta una volta)
        self.assertEqual(len(skipped), 3)
    
    def test_delete_all_rules(self):
        """Verifica che tutte le regole vengano eliminate correttamente."""
        success, not_removed = self.lynis.delete_all_rules()
        self.assertTrue(success)
        self.assertEqual(len(not_removed), 0)
        skipped = self.lynis.read_skipped_list()
        self.assertEqual(len(skipped), 0)
    
    def test_is_rule_skipped(self):
        """Verifica che il controllo delle regole funzioni correttamente."""
        self.assertTrue(self.lynis.is_rule_skipped("TEST-001"))
        self.assertFalse(self.lynis.is_rule_skipped("NON-EXISTENT"))
    
    def test_find_rules_by_pattern(self):
        """Verifica la ricerca delle regole per pattern."""
        self.lynis.add_rules(["PHP-001", "PHP-002", "SEC-003"])
        php_rules = self.lynis.find_rules_by_pattern("PHP")
        self.assertEqual(len(php_rules), 2)
        self.assertIn("PHP-001", php_rules)
        self.assertIn("PHP-002", php_rules)

if __name__ == "__main__":
    lynis = TestLynis()
    lynis.setUp()
    lynis.test_read_skipped_list()
    lynis.test_add_rules()
    lynis.test_delete_all_rules()
    lynis.test_add_duplicate_rule()
    lynis.tearDown()


