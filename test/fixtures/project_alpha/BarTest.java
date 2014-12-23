import static org.junit.Assert.assertEquals;
import org.junit.Test;

public class BarTest {
    @Test
    public void stupidSuccess() {
        assertEquals(5, 5);
    }

    @Test
    public void stupidFail() {
        assertEquals(5, 4);
    }
}