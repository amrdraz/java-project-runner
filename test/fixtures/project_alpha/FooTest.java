import static org.junit.Assert.assertEquals;
import org.junit.Test;
public class FooTest {

    @Test
    public void shouldAlwaysReturnFive() {
        assertEquals(Foo.returnAFive(), 5);
    }
}
